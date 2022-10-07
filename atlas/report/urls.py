from django.urls import path

from . import apps
from .views import views

app_name = apps.ReportConfig.name

urlpatterns = [
    path("<int:pk>", views.ReportDetails.as_view(), name="item"),
    path("<int:pk>/edit", views.ReportEdit.as_view(), name="edit"),
    path("<int:pk>/profile", views.profile, name="profile"),
    path(
        "<int:pk>/maint_status", views.MaintenanceStatus.as_view(), name="maint_status"
    ),
    path("<int:report_id>/image/<int:pk>", views.image, name="image"),
    path("<int:report_id>/image", views.image, name="first_image"),
    path("file/<int:pk>", views.Attachment.as_view(), name="attachment")
    # mini snippet of report with run links.
    # path("<int:pk>/snippet", views.snippet, name="snippet"),
]
