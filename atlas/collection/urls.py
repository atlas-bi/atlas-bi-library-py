from django.urls import path

from . import apps
from .views import views

app_name = apps.CollectionConfig.name

urlpatterns = [
    # base urls
    path("", views.CollectionList.as_view(), name="list"),
    path("<int:pk>", views.CollectionDetails.as_view(), name="item"),
    path("new", views.CollectionNew.as_view(), name="new"),
    path("<int:pk>/edit", views.CollectionDetails.as_view(), name="edit"),
    path("<int:pk>/delete", views.CollectionDelete.as_view(), name="delete"),
    # linked reports
    path(
        "<int:collection_id>/edit/reports/<int:pk>",
        views.ReportLinkNew.as_view(),
        name="report_edit",
    ),
    path(
        "<int:collection_id>/edit/reports",
        views.ReportLinkNew.as_view(),
        name="reports",
    ),
    path(
        "<int:collection_id>/edit/reports/<int:pk>/delete",
        views.ReportLinkDelete.as_view(),
        name="report_delete",
    ),
    # linked terms
    path(
        "<int:collection_id>/edit/terms/<int:pk>",
        views.TermLinkNew.as_view(),
        name="term_edit",
    ),
    path("<int:collection_id>/edit/terms", views.TermLinkNew.as_view(), name="terms"),
    path(
        "<int:collection_id>/edit/terms/<int:pk>/delete",
        views.TermLinkDelete.as_view(),
        name="term_delete",
    ),
]
