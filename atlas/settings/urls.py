from django.urls import path

from . import apps
from .views import theme, views

app_name = apps.SettingsConfig.name

urlpatterns = [
    path("", views.index, name="index"),
    path("roles", views.index, name="roles"),
    path("user_roles", views.index, name="user_roles"),
    path("group_roles", views.index, name="group_roles"),
    path("site_messages", views.index, name="site_messages"),
    path("tags", views.index, name="tags"),
    path("search", views.index, name="search"),
    path("theme", theme.Index.as_view(), name="theme"),
    path("etl", views.index, name="etl"),
]
