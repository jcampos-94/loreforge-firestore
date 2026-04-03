from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import Faction, Character
from .forms import FactionForm, CharacterForm
from .firebase_config import db


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

            # Create faction document
            faction_ref = db.collection("factions").add(
                {"name": faction_name, "leader_name": leader_name}
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
    # Optimize query by loading related faction and mentor in one go
    characters = Character.objects.select_related("faction", "mentor").all()
    return render(request, "loreforge/characters.html", {"characters": characters})


# Create a new character (form handling)
def add_character(request):
    if request.method == "POST":
        form = CharacterForm(request.POST)  # Bind submitted data
        if form.is_valid():
            character = form.save()  # Save character
            return redirect("characters_list")
    else:
        form = CharacterForm()  # Empty form for GET request

    return render(request, "loreforge/add_character.html", {"form": form})


# Delete a character with mentorship and leadership handling
def delete_character(request, character_id):
    character = get_object_or_404(Character, id=character_id)
    faction = character.faction

    # Check if character is leader and store their mentor
    is_leader = faction.leader == character
    mentor = character.mentor

    if request.method == "POST":
        # STEP 1 — RReassign students to the deleted character's mentor
        students = Character.objects.filter(mentor=character)

        for student in students:
            student.mentor = mentor  # inherit mentor
            student.save()

        # STEP 2 — Delete Character
        character.delete()

        # STEP 3 — Handle leader reassignment
        remaining_members = Character.objects.filter(faction=faction)

        if is_leader:
            if not remaining_members.exists():
                # If no members remain, delete faction
                faction.delete()
            else:
                # Promote first available member as new leader
                new_leader = remaining_members.first()
                faction.leader = new_leader
                new_leader.role = f"Leader of the {faction.name}"
                new_leader.save()
                faction.save()

        return redirect("characters_list")

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
