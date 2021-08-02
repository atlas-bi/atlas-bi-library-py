from django.urls import path

from . import apps, views

app_name = apps.ReportConfig.name

urlpatterns = [
    path("<int:pk>", views.index, name="index"),
    path("<int:pk>/comments", views.comments, name="comments"),
    path("<int:pk>/profile", views.profile, name="profile"),
    path("<int:pk>/maint_status", views.maint_status, name="maint_status"),
    path("<int:pk>/image/<int:image_id>", views.image, name="image"),
]
