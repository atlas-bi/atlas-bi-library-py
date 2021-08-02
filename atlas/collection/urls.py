from django.urls import path

from . import apps
from .views import views
from .views.comments import Comments, comments_delete

app_name = apps.CollectionConfig.name

urlpatterns = [
    path("", views.index, name="list"),
    path("<int:collection_id>", views.item, name="details"),
    path("<int:pk>/comments", Comments.as_view(), name="comments"),
    path(
        "<int:pk>/comments/<int:comment_id>/delete",
        comments_delete,
        name="comments_delete",
    ),
    # linked reports
    path("<int:collection_id>/edit/reports", views.reports, name="reports"),
    path(
        "<int:collection_id>/edit/reports/<int:annotation_id>/delete",
        views.reports_delete,
        name="reports_delete",
    ),
    path(
        "<int:collection_id>/edit/reports/<int:annotation_id>",
        views.reports,
        name="reports_edit",
    ),
    # linked terms
    path("<int:collection_id>/edit/terms", views.terms, name="terms"),
    path(
        "<int:collection_id>/edit/terms/<int:annotation_id>/delete",
        views.terms_delete,
        name="terms_delete",
    ),
    path(
        "<int:collection_id>/edit/terms/<int:annotation_id>",
        views.terms,
        name="terms_edit",
    ),
    path("new", views.edit, name="edit"),
    path("<int:collection_id>/edit", views.edit, name="edit"),
    path("<int:collection_id>/delete", views.delete, name="delete"),
]
