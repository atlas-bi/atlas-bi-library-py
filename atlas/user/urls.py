from django.urls import path

from . import views

urlpatterns = [
    path("roles", views.roles, name="roles"),
    path("roles/change", views.change_role, name="change role"),
    path(
        "preference/video/<int:state>", views.preference_video, name="preference video"
    ),
]
