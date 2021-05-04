from django.urls import path

from . import views

urlpatterns = [
    path("<int:report_id>", views.index, name="index"),
    path("<int:report_id>/comments", views.comments, name="comments"),
    path("<int:report_id>/maint_status", views.maint_status, name="maint_status"),
    path("<int:report_id>/image/<int:image_id>", views.image, name="image"),
]
