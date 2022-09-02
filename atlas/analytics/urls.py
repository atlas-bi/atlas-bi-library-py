from django.urls import path

from . import apps, views, visits

app_name = apps.AnalyticsConfig.name

urlpatterns = [
    path("", views.index, name="index"),
    path("log", views.log, name="log"),
    path("trace", views.trace, name="trace"),
    path("error", views.error, name="error"),
    path("visits", visits.index, name="visits"),
    path("visits/browsers", visits.browsers, name="browsers"),
    path("visits/os", visits.os, name="os"),
    path("visits/resolution", visits.resolution, name="resolution"),
    path("visits/users", visits.users, name="users"),
    path("visits/load_time", visits.load_time, name="load_time"),
]
