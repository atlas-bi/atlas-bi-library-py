from django.urls import path

from . import apps
from .views import views
from .views.comments import Comments, comments_delete

app_name = apps.CollectionConfig.name

urlpatterns = [
    path("", views.CollectionList.as_view(), name="list"),
    path("<int:pk>", views.CollectionDetails.as_view(), name="item"),
    path("<int:pk>/comments", Comments.as_view(), name="comments"),
    path(
        "<int:pk>/comments/<int:comment_id>/delete",
        comments_delete,
        name="comment_delete",
    ),
    # linked reports
    path("<int:pk>/edit/reports", views.reports, name="reports"),
    path(
        "<int:pk>/edit/reports/<int:annotation_id>/delete",
        views.reports_delete,
        name="report_delete",
    ),
    path(
        "<int:pk>/edit/reports/<int:annotation_id>",
        views.reports,
        name="report_edit",
    ),
    # linked terms
    path("<int:pk>/edit/terms", views.terms, name="terms"),
    path(
        "<int:pk>/edit/terms/<int:annotation_id>/delete",
        views.terms_delete,
        name="term_delete",
    ),
    path(
        "<int:pk>/edit/terms/<int:annotation_id>",
        views.terms,
        name="term_edit",
    ),
    path("new", views.CollectionNew.as_view(), name="new"),
    path("<int:pk>/edit", views.CollectionDetails.as_view(), name="edit"),
    path("<int:pk>/delete", views.delete, name="delete"),
]
