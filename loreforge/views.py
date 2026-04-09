from django.shortcuts import render, redirect
from .forms import FactionForm, CharacterForm
from .firebase_config import db
from datetime import datetime, UTC


# Main page (landing view)
def home(request):
    logs = []

    for doc in db.collection("activity_logs").stream():
        log = doc.to_dict()
        log["id"] = doc.id
        logs.append(log)

    logs.sort(key=lambda log: log.get("created_at", ""), reverse=True)

    return render(request, "loreforge/home.html", {"logs": logs[:5]})


# Display all factions
def factions_list(request):
    faction_docs = db.collection("factions").stream()

    factions = []

    for doc in faction_docs:
        faction_data = doc.to_dict()
        faction_data["id"] = doc.id
        factions.append(faction_data)

    return render(request, "loreforge/factions.html", {"factions": factions})


# Create a new faction
def add_faction(request):
    if request.method == "POST":
        form = FactionForm(request.POST)

        if form.is_valid():
            faction_name = form.cleaned_data["name"]
            leader_name = form.cleaned_data["leader_name"]

            # Create faction first
            faction_ref = db.collection("factions").add(
                {"name": faction_name, "leader_name": leader_name}
            )

            faction_id = faction_ref[1].id

            # Create faction leader automatically
            db.collection("characters").add(
                {
                    "name": leader_name,
                    "role": f"Leader of the {faction_name}",
                    "faction_id": faction_id,
                    "mentor_id": None,
                    "created_at": datetime.now(UTC).isoformat(),
                }
            )

            log_activity(
                "New Faction Rises",
                f"The {faction_name} has emerged under the leadership of {leader_name}.",
            )

            return redirect("factions_list")
    else:
        form = FactionForm()

    return render(
        request,
        "loreforge/add_faction.html",
        {"form": form, "button_text": "Create Faction"},
    )


# Edit a faction
def edit_faction(request, faction_id):
    faction_ref = db.collection("factions").document(faction_id)
    faction_doc = faction_ref.get()

    if not faction_doc.exists:
        return redirect("factions_list")

    faction_data = faction_doc.to_dict()

    if request.method == "POST":
        form = FactionForm(request.POST)

        if form.is_valid():
            faction_name = form.cleaned_data["name"]
            leader_name = form.cleaned_data["leader_name"]

            faction_ref.update({"name": faction_name, "leader_name": leader_name})

            return redirect("factions_list")

    else:
        form = FactionForm(
            initial={
                "name": faction_data.get("name", ""),
                "leader_name": faction_data.get("leader_name", ""),
            }
        )

    return render(
        request,
        "loreforge/add_faction.html",
        {"form": form, "button_text": "Edit Faction"},
    )


# Delete a faction (with confirmation)
def delete_faction(request, faction_id):
    faction_ref = db.collection("factions").document(faction_id)
    faction = faction_ref.get()

    if not faction.exists:
        return redirect("factions_list")

    faction = faction.to_dict()
    faction["id"] = faction_id

    # Find all members of this faction
    members = []

    for doc in db.collection("characters").stream():
        character = doc.to_dict()

        if character.get("faction_id") == faction_id:
            character["id"] = doc.id
            members.append(character)

    if request.method == "POST":
        # Delete all members first
        for member in members:
            db.collection("characters").document(member["id"]).delete()

        # Delete faction
        faction_ref.delete()

        log_activity(
            "War Tragedy",
            f"The {faction['name']} and all its members have joined their ancestors after honorable combat.",
        )

        return redirect("factions_list")

    # Show confirmation page with warning
    return render(
        request,
        "loreforge/delete_faction.html",
        {"faction": faction, "members": members},
    )


# Display all characters
def characters_list(request):
    character_docs = db.collection("characters").stream()

    characters = []

    for doc in character_docs:
        character = doc.to_dict()
        character["id"] = doc.id

        # Resolve Faction name
        faction_id = character.get("faction_id")
        if faction_id:
            faction_doc = db.collection("factions").document(faction_id).get()
            if faction_doc.exists:
                character["faction_name"] = faction_doc.to_dict().get("name")
            else:
                character["faction_name"] = "Uknown"
        else:
            character["faction_name"] = "Uknown"

        # Resolve Mentor name
        mentor_id = character.get("mentor_id")
        if mentor_id:
            mentor_doc = db.collection("characters").document(mentor_id).get()
            if mentor_doc.exists:
                character["mentor_name"] = mentor_doc.to_dict().get("name")
            else:
                character["mentor_name"] = "Uknown"
        else:
            character["mentor_name"] = "Unknown"

        characters.append(character)

    return render(request, "loreforge/characters.html", {"characters": characters})


# Create a new character
def add_character(request):
    if request.method == "POST":
        form = CharacterForm(request.POST)

        if form.is_valid():
            db.collection("characters").add(
                {
                    "name": form.cleaned_data["name"],
                    "role": form.cleaned_data["role"],
                    "faction_id": form.cleaned_data["faction"],
                    "mentor_id": form.cleaned_data["mentor"] or None,
                    "created_at": datetime.now(UTC).isoformat(),
                }
            )

            mentor_text = ""
            if form.cleaned_data["mentor"]:
                mentor_doc = (
                    db.collection("characters")
                    .document(form.cleaned_data["mentor"])
                    .get()
                )

                if mentor_doc.exists:
                    mentor_name = mentor_doc.to_dict().get("name")
                    mentor_text = f", mentored by {mentor_name}"

            faction_name = get_faction_name(form.cleaned_data["faction"])

            log_activity(
                "New Hero",
                f"{form.cleaned_data["name"]} joined the {faction_name} as {form.cleaned_data["role"]}{mentor_text}.",
            )

            return redirect("characters_list")
    else:
        form = CharacterForm()

    return render(
        request,
        "loreforge/add_character.html",
        {"form": form, "button_text": "Create Character"},
    )


# Edit a character
def edit_character(request, character_id):
    character_doc = db.collection("characters").document(character_id).get()

    if not character_doc.exists:
        return redirect("characters_list")

    character = character_doc.to_dict()

    if request.method == "POST":
        form = CharacterForm(request.POST)

        if form.is_valid():
            db.collection("characters").document(character_id).update(
                {
                    "name": form.cleaned_data["name"],
                    "role": form.cleaned_data["role"],
                    "faction_id": form.cleaned_data["faction"],
                    "mentor_id": form.cleaned_data["mentor"] or None,
                }
            )

            mentor_text = ""
            if form.cleaned_data["mentor"]:
                mentor_doc = (
                    db.collection("characters")
                    .document(form.cleaned_data["mentor"])
                    .get()
                )

                if mentor_doc.exists:
                    mentor_name = mentor_doc.to_dict().get("name")
                    mentor_text = f", mentored by {mentor_name}"

            faction_name = get_faction_name(form.cleaned_data["faction"])

            log_activity(
                "Status Change",
                f"{form.cleaned_data["name"]} is now a {form.cleaned_data["role"]} of the {faction_name}{mentor_text}.",
            )

            return redirect("characters_list")

    else:
        form = CharacterForm(
            initial={
                "name": character.get("name"),
                "role": character.get("role"),
                "faction": character.get("faction_id"),
                "mentor": character.get("mentor_id"),
            }
        )

    return render(
        request,
        "loreforge/add_character.html",
        {"form": form, "button_text": "Edit Character"},
    )


# Delete a character with mentorship and leadership handling
def delete_character(request, character_id):
    character_ref = db.collection("characters").document(character_id)
    character_doc = character_ref.get()

    if not character_doc.exists:
        return redirect("characters_list")

    character = character_doc.to_dict()
    character["id"] = character_id

    if request.method == "POST":
        faction_id = character.get("faction_id")
        deleted_name = character.get("name")
        deleted_mentor_id = character.get("mentor_id")

        faction_ref = db.collection("factions").document(faction_id)
        faction_doc = faction_ref.get()

        faction_data = faction_doc.to_dict() if faction_doc.exists else None
        is_leader = faction_data and faction_data.get("leader_name") == deleted_name

        # STEP 1 — Reassign students
        student_docs = db.collection("characters").stream()

        for doc in student_docs:
            student = doc.to_dict()

            if student.get("mentor_id") == character_id:
                db.collection("characters").document(doc.id).update(
                    {"mentor_id": deleted_mentor_id}
                )

        # STEP 2 — Delete Character
        character_ref.delete()

        log_activity(
            "Missing in Action",
            f"{deleted_name} did not return home after the last battle.",
        )

        # STEP 3 — Handle leader reassignment
        if is_leader:
            remaining_members = []

            for doc in db.collection("characters").stream():
                member = doc.to_dict()

                if member.get("faction_id") == faction_id:
                    remaining_members.append(
                        {
                            "doc_id": doc.id,
                            "name": member.get("name"),
                            "role": member.get("role"),
                            "created_at": member.get("created_at", ""),
                        }
                    )

            if not remaining_members:
                faction_ref.delete()
            else:
                remaining_members.sort(key=lambda member: member.get("created_at", ""))
                new_leader = remaining_members[0]

                db.collection("characters").document(new_leader["doc_id"]).update(
                    {"role": f"Leader of the {faction_data['name']}"}
                )

                faction_ref.update({"leader_name": new_leader["name"]})

        return redirect(characters_list)

    return render(request, "loreforge/delete_character.html", {"character": character})


# Recursively build mentorship hierarchy
def build_tree(character_id):
    character_doc = db.collection("characters").document(character_id).get()

    if not character_doc.exists:
        return None

    character = character_doc.to_dict()
    character["id"] = character_id

    students = []

    # Find all direct students
    for doc in db.collection("characters").stream():
        student = doc.to_dict()

        if student.get("mentor_id") == character_id:
            subtree = build_tree(doc.id)

            if subtree:
                students.append(subtree)

    return {
        "character": character,
        "students": students,
    }


# Display mentorship tree starting from a character
def mentorship_tree(request, character_id):
    tree = build_tree(character_id)

    if not tree:
        return redirect("characters_list")

    return render(request, "loreforge/mentorship_tree.html", {"tree": tree})


# Save an event entry to the Firestore activity log
def log_activity(action, details):
    db.collection("activity_logs").add(
        {
            "action": action,
            "details": details,
            "created_at": datetime.now(UTC).isoformat(),
        }
    )


# Helper function to retrieve a faction name from Firestore by ID
def get_faction_name(faction_id):
    faction_doc = db.collection("factions").document(faction_id).get()

    if faction_doc.exists:
        return faction_doc.to_dict().get("name", "Unknown Faction")

    return "Unknown Faction"
