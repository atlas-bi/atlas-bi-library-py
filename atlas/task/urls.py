from django.urls import path

from . import apps, views

app_name = apps.TaskConfig.name

urlpatterns = [
    path("", views.index, name="index"),
]
