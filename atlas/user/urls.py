from django.urls import path

from . import apps, stars, views

app_name = apps.UserConfig.name

urlpatterns = [
    path("", views.index, name="me"),
    path("<int:pk>", views.index, name="profile"),
    path("<int:pk>/image", views.image, name="image"),
    path("stars", stars.index, name="stars"),
    path("<int:pk>/stars", stars.index, name="stars"),
    path("stars/edit", stars.edit, name="stars_edit"),
    path("groups", views.groups, name="groups"),
    path("<int:pk>/groups", views.groups, name="groups"),
    path("subscriptions", views.subscriptions, name="subscriptions"),
    path("<int:pk>/subscriptions", views.subscriptions, name="subscriptions"),
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
    path("roles", views.roles, name="roles"),
    path("settings/disable_admin", views.disable_admin, name="disable_admin"),
]
