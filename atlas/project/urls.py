from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:project_id>", views.item, name="item"),
    path("<int:project_id>/comments", views.comments, name="comments"),
    path(
        "<int:project_id>/comments/<int:comment_id>/delete",
        views.comments_delete,
        name="delete comments",
    ),
    # linked reports
    path("<int:project_id>/edit/reports", views.reports, name="reports"),
    path(
        "<int:project_id>/edit/reports/<int:annotation_id>/delete",
        views.reports_delete,
        name="reports_delete",
    ),
    path(
        "<int:project_id>/edit/reports/<int:annotation_id>",
        views.reports,
        name="reports_edit",
    ),
    # linked terms
    path("<int:project_id>/edit/terms", views.terms, name="terms"),
    path(
        "<int:project_id>/edit/terms/<int:annotation_id>/delete",
        views.terms_delete,
        name="terms_delete",
    ),
    path(
        "<int:project_id>/edit/terms/<int:annotation_id>",
        views.terms,
        name="terms_edit",
    ),
    path("new", views.edit, name="edit"),
    path("<int:project_id>/edit", views.edit, name="edit"),
    path("<int:project_id>/delete", views.delete, name="delete"),
]
