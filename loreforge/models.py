from django.db import models


# Faction model (represents a group of characters)
class Faction(models.Model):
    # Unique faction name
    name = models.CharField(max_length=100, unique=True)

    # Leader is a Character (can be null if not assigned yet)
    # SET_NULL ensures faction is not deleted if leader is removed
    leader = models.ForeignKey(
        "Character",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="leading_faction",  # Reverse relation from Character
    )

    # String representation (used in admin and dropdowns)
    def __str__(self):
        return self.name


# Character model (represents an individual entity)
class Character(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)

    # Each character belongs to a faction
    # CASCADE deletes characters if the faction is deleted
    faction = models.ForeignKey(
        Faction,
        on_delete=models.CASCADE,
        related_name="members",  # Access faction.members
    )

    # Self-referencing relationship for mentorship
    # Allows building hierarchical mentor-student trees
    mentor = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",  # Access character.students
    )

    # String representation (used in admin and dropdowns)
    def __str__(self):
        return self.name
