from django.urls import path

from . import apps
from .views import errors, trace, views, visits

app_name = apps.AnalyticsConfig.name

urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("log", views.log, name="log"),
    path("trace", trace.Index.as_view(), name="trace"),
    path("trace/log", trace.log, name="trace_log"),
    path("trace/<int:pk>", trace.Index.as_view(), name="trace"),
    path("error", errors.Index.as_view(), name="error"),
    path("error/<int:pk>", errors.Index.as_view(), name="error"),
    path("visits", visits.Index.as_view(), name="visits"),
    path("visits/browsers", visits.Browsers.as_view(), name="browsers"),
    path("visits/os", visits.Os.as_view(), name="os"),
    path("visits/resolution", visits.Resolution.as_view(), name="resolution"),
    path("visits/users", visits.UserAnalytics.as_view(), name="users"),
    path("visits/load_time", visits.LoadTime.as_view(), name="load_time"),
]
