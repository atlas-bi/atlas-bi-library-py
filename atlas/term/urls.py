from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:term_id>", views.item, name="item"),
    path("<int:term_id>/comments", views.comments, name="comments"),
    path(
        "<int:term_id>/comments/<int:comment_id>/delete",
        views.comments_delete,
        name="delete comments",
    ),
    path("new", views.edit, name="edit"),
    path("<int:term_id>/edit", views.edit, name="edit"),
    path("<int:term_id>/delete", views.delete, name="delete"),
]
