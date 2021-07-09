# pylint: disable=C0103,C0114

from django.urls import path
from term import apps
from term.views import views
from term.views.comments import Comments, comments_delete

app_name = apps.TermConfig.name

urlpatterns = [
    path("", views.TermList.as_view(), name="list"),
    path("<int:pk>", views.TermDetails.as_view(), name="details"),
    path("<int:pk>/comments", Comments.as_view(), name="comments"),
    path(
        "<int:pk>/comments/<int:comment_id>/delete",
        comments_delete,
        name="comments_delete",
    ),
    path("new", views.TermNew.as_view(), name="new"),
    path("<int:pk>/edit", views.TermDetails.as_view(), name="edit"),
    path("<int:pk>/delete", views.delete, name="delete"),
]
