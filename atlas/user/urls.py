from django.urls import path

from . import apps, views

app_name = apps.UserConfig.name

urlpatterns = [
    path("", views.index, name="me"),
    path("<int:pk>", views.index, name="profile"),
    path("favorites", views.favorites, name="favorites"),
    path(
        "favorites_create_folder",
        views.favorites_create_folder,
        name="favorites_create_folder",
    ),
    path(
        "favorites_delete_folder",
        views.favorites_delete_folder,
        name="ffavorites_delete_folder",
    ),
    path(
        "favorites_reorder_folder",
        views.favorites_reorder_folder,
        name="favorites_reorder_folder",
    ),
    path("favorites_reorder", views.favorites_reorder, name="favorites_reorder"),
    path(
        "favorites_change_folder",
        views.favorites_change_folder,
        name="favorites_change_folder",
    ),
    path("roles", views.roles, name="roles"),
    path("roles/change", views.change_role, name="change_role"),
    path(
        "preference/video/<int:state>", views.preference_video, name="preference_video"
    ),
]
