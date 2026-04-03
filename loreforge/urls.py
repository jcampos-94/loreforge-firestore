from django.urls import path
from . import views

urlpatterns = [
    # Main URL
    path("", views.home, name="home"),
    # Faction List Url
    path("factions/", views.factions_list, name="factions_list"),
    # Add Faction Form Url
    path("add-faction/", views.add_faction, name="add_faction"),
    # Edit Faction Form Url
    path("edit-faction/<str:faction_id>/", views.edit_faction, name="edit_faction"),
    # Delete Faction Form Url
    path(
        "delete-faction/<str:faction_id>/", views.delete_faction, name="delete_faction"
    ),
    # Character List Url
    path("characters/", views.characters_list, name="characters_list"),
    # Add Character Form Url
    path("add-character/", views.add_character, name="add_character"),
    # Delete Character Form Url
    path(
        "delete-character/<int:character_id>/",
        views.delete_character,
        name="delete_character",
    ),
    # Mentorship Tree Url
    path(
        "mentorship-tree/<int:character_id>/",
        views.mentorship_tree,
        name="mentorship_tree",
    ),
]
