from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="user profile"),
    path("favorites", views.favorites, name="favorites"),
    path(
        "favorites_create_folder",
        views.favorites_create_folder,
        name="favorites create folder",
    ),
    path(
        "favorites_delete_folder",
        views.favorites_delete_folder,
        name="favorites delete folder",
    ),
    path(
        "favorites_reorder_folder",
        views.favorites_reorder_folder,
        name="favorites reorder folder",
    ),
    path("favorites_reorder", views.favorites_reorder, name="favorites reorder"),
    path(
        "favorites_change_folder",
        views.favorites_change_folder,
        name="favorites change folder",
    ),
    path("roles", views.roles, name="roles"),
    path("roles/change", views.change_role, name="change role"),
    path(
        "preference/video/<int:state>", views.preference_video, name="preference video"
    ),
]
