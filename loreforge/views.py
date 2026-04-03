from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import Faction, Character
from .forms import FactionForm, CharacterForm
from .firebase_config import db
from datetime import datetime, UTC


# Main page (landing view)
def home(request):
    return render(request, "loreforge/home.html")


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

    faction_data = faction.to_dict()
    faction_data["id"] = faction.id

    if request.method == "POST":
        faction_ref.delete()
        return redirect("factions_list")

    # Show confirmation page with warning
    return render(
        request,
        "loreforge/delete_faction.html",
        {"faction": faction_data},
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


# Create a new character (form handling)
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

            return redirect("characters_list")
    else:
        form = CharacterForm()

    return render(
        request,
        "loreforge/add_character.html",
        {"form": form, "button_text": "Create Character"},
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
def build_tree(character):
    # Get all direct students of this character
    students = Character.objects.filter(mentor=character)

    return {
        "character": character,
        # Recursively build subtree for each student
        "students": [build_tree(student) for student in students],
    }


# Display mentorship tree starting from a character
def mentorship_tree(request, character_id):
    character = get_object_or_404(Character, id=character_id)
    tree = build_tree(character)  # Build full hierarchy

    return render(request, "loreforge/mentorship_tree.html", {"tree": tree})
