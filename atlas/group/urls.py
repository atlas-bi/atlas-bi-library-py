from django.urls import path

from . import apps, views

app_name = apps.GroupConfig.name

urlpatterns = [
    path("<int:pk>", views.GroupDetails.as_view(), name="profile"),
]
