from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:term_id>", views.item, name="item"),
    path("<int:term_id>/comments", views.comments, name="comments"),
]
