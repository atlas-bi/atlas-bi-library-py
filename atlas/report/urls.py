from django.urls import path

from . import apps
from .views import views
from .views.comments import Comments, comments_delete

app_name = apps.ReportConfig.name

urlpatterns = [
    path("<int:pk>", views.index, name="index"),
    path("<int:pk>/profile", views.profile, name="profile"),
    path("<int:pk>/maint_status", views.maint_status, name="maint_status"),
    path("<int:report_id>/image/<int:pk>", views.image, name="image"),
    path("<int:report_id>/image", views.image, name="first_image"),
    # mini snippet of report with run links.
    # path("<int:pk>/snippet", views.snippet, name="snippet"),
    # comments
    path("<int:pk>/comments", Comments.as_view(), name="comments"),
    path(
        "<int:pk>/comments/<int:comment_id>/delete",
        comments_delete,
        name="comments_delete",
    ),
]
