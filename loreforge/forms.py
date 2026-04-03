from django import forms
from django.core.exceptions import ValidationError
from .models import Faction, Character
from .firebase_config import db


# Helper: format names (trim + Title Case)
def format_name(value):
    words = value.strip().lower().split(" ")
    return " ".join(word.capitalize() for word in words)


# Faction Form
class FactionForm(forms.ModelForm):
    # Extra field (not in model) to create leader
    leader_name = forms.CharField(max_length=100)

    class Meta:
        model = Faction
        fields = ["name", "leader_name"]

    # Format faction name
    def clean_name(self):
        return format_name(self.cleaned_data["name"])

    # Format leader name
    def clean_leader_name(self):
        return format_name(self.cleaned_data["leader_name"])

    # Custom save to create leader character automatically
    def save(self, commit=True):
        faction = super().save(commit=False)

        leader_name = self.cleaned_data["leader_name"]

        if commit:
            faction.save()

            # Create leader as a Character
            leader = Character.objects.create(
                name=leader_name, role=f"Leader of the {faction.name}", faction=faction
            )

            # Assign leader to faction
            faction.leader = leader
            faction.save()

        return faction


# Character Form
class CharacterForm(forms.Form):
    name = forms.CharField(max_length=100)
    role = forms.CharField(max_length=100)
    faction = forms.ChoiceField(choices=[])
    mentor = forms.ChoiceField(choices=[], required=False)

    # Dynamically filter mentor choices based on selected faction
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load factions from Firestore
        faction_docs = db.collection("factions").stream()
        faction_choices = [(doc.id, doc.to_dict().get("name")) for doc in faction_docs]
        self.fields["faction"].choices = faction_choices

        # Load characters for mentor dropdown
        character_docs = db.collection("characters").stream()
        mentor_choices = [(doc.id, doc.to_dict().get("name")) for doc in character_docs]

        # Optional empty choice
        mentor_choices.insert(0, ("", "No mentor"))

        self.fields["mentor"].choices = mentor_choices

    # Format character name
    def clean_name(self):
        name = self.cleaned_data["name"]
        return format_name(name)

    # Format role name
    def clean_role(self):
        role = self.cleaned_data["role"]
        return format_name(role)

    # Custom validation rules
    def clean(self):
        cleaned_data = super().clean()

        name = cleaned_data.get("name")
        faction_id = cleaned_data.get("faction")
        mentor_id = cleaned_data.get("mentor")

        # Rules 1-4: Only validate if Mentor was selected
        if mentor_id:
            mentor_doc = db.collection("characters").document(mentor_id).get()

            if not mentor_doc.exists:
                self.add_error("mentor", "Selected mentor does not exist.")
                return cleaned_data

            mentor_data = mentor_doc.to_dict()

            # Rule 1: Mentor must belong to the same faction
            if mentor_data.get("faction_id") != faction_id:
                self.add_error("mentor", "Mentor must belong to the same faction.")

            # Rule 2: Character cannot mentor themselves
            if mentor_data.get("name") == name:
                self.add_error("mentor", "A character cannot mentor themselves.")

            # Rules 3 & 4: Circular / recursive loop detection
            visited = set()
            current_id = mentor_id

            while current_id:
                # Detect circular references
                if current_id in visited:
                    self.add_error(None, "Circular mentorship detected.")
                    break

                visited.add(current_id)

                current_doc = db.collection("characters").document(current_id).get()

                if not current_doc.exists:
                    break

                current_data = current_doc.to_dict()

                # Prevent loops back to the same character
                if current_data.get("name") == name:
                    self.add_error(None, "Mentorship loop detected.")
                    break

                current_id = current_data.get("mentor_id")

        return cleaned_data
