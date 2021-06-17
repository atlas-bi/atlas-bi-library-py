from django.urls import path

from .views import base, initiatives

urlpatterns = [
    path("", base.index, name="index"),
    path("solr_health", base.solr_health, name="solr health"),
    path("celery_health", base.celery_health, name="celery health"),
    path(
        "search/initiatives/<str:arg>",
        initiatives.initiatives,
        name="search initiatives",
    ),
    path("job/<int:job_id>/delete", base.job_edit, name="job edit"),
    path("job/schedule", base.job_schedule, name="job schedule"),
]
