from django.urls import path

from . import apps, views

app_name = apps.InitiativeConfig.name

urlpatterns = [
    path("", views.index, name="list"),
    path("<int:initiative_id>", views.item, name="item"),
    path("new", views.edit, name="edit"),
    path("<int:initiative_id>/edit", views.edit, name="edit"),
    path("<int:initiative_id>/delete", views.delete, name="delete"),
]
