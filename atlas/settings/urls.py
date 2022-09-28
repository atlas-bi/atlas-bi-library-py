from django.urls import path

from . import apps
from .views import group_roles, roles, tags, theme, user_roles, views

app_name = apps.SettingsConfig.name

urlpatterns = [
    path("", views.index, name="index"),
    path("roles", roles.Index.as_view(), name="roles"),
    path("roles/<int:pk>/delete", roles.Delete.as_view(), name="delete_role"),
    path(
        "roles/<int:pk>/permission/<int:permission_pk>",
        roles.Permission.as_view(),
        name="update_permission",
    ),
    path("user_roles", user_roles.Index.as_view(), name="user_roles"),
    path(
        "user_roles/<int:pk>/delete",
        user_roles.Delete.as_view(),
        name="delete_user_role",
    ),
    path("group_roles", group_roles.Index.as_view(), name="group_roles"),
    path(
        "group_roles/<int:pk>/delete",
        group_roles.Delete.as_view(),
        name="delete_group_role",
    ),
    path("tags/<str:tag_type>", tags.Index.as_view(), name="tags"),
    path(
        "tags/<str:tag_type>/delete/<int:pk>", tags.Delete.as_view(), name="tags_delete"
    ),
    path("site_messages", views.index, name="site_messages"),
    path("search", views.index, name="search"),
    path("theme", theme.Index.as_view(), name="theme"),
    path("etl", views.index, name="etl"),
]
