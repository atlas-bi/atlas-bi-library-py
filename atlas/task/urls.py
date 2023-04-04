from django.urls import path

from . import apps, views

app_name = apps.TaskConfig.name

urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("recommend_retire", views.RecommendRetire.as_view(), name="recommend_retire"),
    path("unused", views.Unused.as_view(), name="unused"),
    path(
        "maintenance_required",
        views.MaintenanceRequired.as_view(),
        name="maintenance_required",
    ),
    path("audit_only", views.AuditOnly.as_view(), name="audit_only"),
    path("no_schedule", views.NoSchedule.as_view(), name="no_schedule"),
    path("not_analytics", views.NotAnalytics.as_view(), name="not_analytics"),
    path("top_undocumented", views.TopUndocumented.as_view(), name="top_undocumented"),
    path("new_undocumented", views.NewUndocumented.as_view(), name="new_undocumented"),
]
