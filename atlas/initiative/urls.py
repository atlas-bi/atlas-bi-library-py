from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:initiative_id>", views.item, name="item"),
    path("new", views.edit, name="edit"),
    path("<int:initiative_id>/edit", views.edit, name="edit"),
    path("<int:initiative_id>/delete", views.delete, name="delete"),
]
