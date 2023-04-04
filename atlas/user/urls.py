from django.urls import path

from . import apps
from .views import admin, profile, settings, stars

app_name = apps.UserConfig.name

urlpatterns = [
    path("", profile.Index.as_view(), name="me"),
    path("<int:pk>", profile.Index.as_view(), name="profile"),
    path("stars", stars.index, name="stars"),
    path("<int:pk>/stars", stars.index, name="stars"),
    path("settings", settings.Index.as_view(), name="settings"),
    path("shares", profile.Shares.as_view(), name="shares"),
    path("settings/toggle", settings.Toggle.as_view(), name="toggle"),
    path("stars/edit", stars.edit, name="stars_edit"),
    path("groups", profile.UserGroups.as_view(), name="groups"),
    path("<int:pk>/groups", profile.UserGroups.as_view(), name="groups"),
    path("history", profile.History.as_view(), name="history"),
    path("<int:pk>/history", profile.History.as_view(), name="history"),
    path("subscriptions", profile.Subscriptions.as_view(), name="subscriptions"),
    path(
        "<int:pk>/subscriptions", profile.Subscriptions.as_view(), name="subscriptions"
    ),
    path(
        "stars/folder/create",
        stars.create_folder,
        name="stars_create_folder",
    ),
    path(
        "stars/folder/<int:pk>/edit",
        stars.edit_folder,
        name="stars_edit_folder",
    ),
    path(
        "stars/folder/<int:pk>/delete",
        stars.delete_folder,
        name="fstars_delete_folder",
    ),
    path(
        "stars/folder/reorder",
        stars.reorder_folder,
        name="stars_reorder_folder",
    ),
    path("stars/reorder", stars.reorder, name="stars_reorder"),
    path(
        "stars/folder/change",
        stars.change_folder,
        name="stars_change_folder",
    ),
    path("roles", admin.roles, name="roles"),
    path("settings/disable_admin", admin.disable_admin, name="disable_admin"),
]
