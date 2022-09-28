from django.urls import path

from . import apps
from .views import (
    base,
    collections,
    groups,
    initiatives,
    lookups,
    reports,
    terms,
    users,
)

app_name = apps.EtlConfig.name

urlpatterns = [
    path("", base.index, name="index"),
    path("solr_health", base.solr_health, name="solr_health"),
    path("celery_health", base.celery_health, name="celery_health"),
    path(
        "search/initiatives/<str:arg>",
        initiatives.initiatives,
        name="search_initiatives",
    ),
    path(
        "search/users/<str:arg>",
        users.users,
        name="search_users",
    ),
    path(
        "search/groups/<str:arg>",
        groups.groups,
        name="search_groups",
    ),
    path(
        "search/collections/<str:arg>",
        collections.collections,
        name="search_collections",
    ),
    path(
        "search/terms/<str:arg>",
        terms.terms,
        name="search_terms",
    ),
    path(
        "search/reports/<str:arg>",
        reports.reports,
        name="search_reports",
    ),
    path(
        "search/lookups/<str:arg>",
        lookups.lookups,
        name="search_lookups",
    ),
    path("job/<int:job_id>/delete", base.job_delete, name="job_delete"),
    path("job/schedule", base.job_schedule, name="job_schedule"),
]
