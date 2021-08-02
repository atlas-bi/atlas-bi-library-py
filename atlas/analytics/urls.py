from django.urls import path

from . import apps, views

app_name = apps.AnalyticsConfig.name

urlpatterns = [
    path("", views.index, name="index"),
    path("log", views.log, name="log"),
]
