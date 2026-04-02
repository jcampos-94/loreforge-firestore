from django import forms
from django.core.exceptions import ValidationError
from .models import Faction, Character


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
class CharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = ["name", "role", "faction", "mentor"]

    # Dynamically filter mentor choices based on selected faction
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Character.objects.all()

        if "faction" in self.data:
            try:
                faction_id = int(self.data.get("faction"))
                filtered = Character.objects.filter(faction_id=faction_id)

                # Include currently selected mentor (prevents validation issues)
                mentor_id = self.data.get("mentor")
                if mentor_id:
                    queryset = (
                        filtered | Character.objects.filter(id=mentor_id)
                    ).distinct()
                else:
                    queryset = filtered

            except (ValueError, TypeError):
                pass

        self.fields["mentor"].queryset = queryset

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
        faction = cleaned_data.get("faction")
        mentor = cleaned_data.get("mentor")

        # Rule 1: Mentor must belong to the same faction
        if mentor and faction and mentor.faction != faction:
            self.add_error("mentor", "Mentor must belong to the same faction.")

        # Rule 2: Character cannot mentor themselves
        if mentor and name and mentor.name == name:
            self.add_error("mentor", "A character cannot mentor themselves.")

        # Rules 3 & 4: Prevent circular and recursive loops
        if mentor:
            visited = set()
            current = mentor

            while current:
                # Detect circular references
                if current in visited:
                    self.add_error(None, "Circular mentorship detected.")

                # Prevent loops back to the same character
                if current.name == name:
                    self.add_error(None, "Mentorship loop detected.")

                visited.add(current)
                current = current.mentor

        return cleaned_data
