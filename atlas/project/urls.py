from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:project_id>", views.item, name="item"),
    path("<int:project_id>/comments", views.comments, name="comments"),
]
