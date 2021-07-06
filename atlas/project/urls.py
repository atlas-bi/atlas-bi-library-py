from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:project_id>", views.item, name="item"),
    path("<int:project_id>/comments", views.comments, name="comments"),
    path("new", views.edit, name="edit"),
    path("<int:project_id>/edit", views.edit, name="edit"),
    path("<int:project_id>/delete", views.delete, name="delete"),
]
