"""Atlas ETL for Search."""
import json
import logging

import pysolr
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django_celery_beat.models import PeriodicTask
from django_celery_results.models import TaskResult

from atlas.celery import app as celery_app


@never_cache
def solr_health(request: HttpRequest) -> JsonResponse:
    """Solr Search health check."""
    try:
        solr = pysolr.Solr(settings.SOLR_URL)

        solr_status = json.loads(solr.ping())

        return JsonResponse(
            {
                "message": "Ping: %sms; Status: %s"
                % (
                    solr_status["responseHeader"]["QTime"],
                    solr_status["status"],
                ),
                "status": "success",
            }
        )
    except pysolr.SolrError as e:
        logging.error(str(e))
        return JsonResponse({"message": "Offline", "status": "error"})


@never_cache
def celery_health(request: HttpRequest) -> JsonResponse:
    """Celery worker health check."""
    try:
        insp = celery_app.control.inspect()
        nodes = insp.stats()
        if not nodes:
            raise Exception("Not running.")
        logging.debug("Celery workers are: {}".format(nodes))
        return JsonResponse({"message": "Online", "status": "success"})

    except Exception as e:
        logging.error(str(e))
        return JsonResponse({"message": "Offline", "status": "error"})


def index(request: HttpRequest) -> JsonResponse:
    """Atlas ETL Dashboard."""
    context = {
        "history": [result.as_dict() for result in TaskResult.objects.all()[:10]],
        "title": "ETL",
        "search_etls": [
            "reports",
            "collections",
            "terms",
            "initiatives",
            "users",
            "lookups",
            "groups",
        ],
    }

    return render(request, "etl/index.html.dj", context)


@never_cache
def job_delete(request: HttpRequest, job_id: int) -> HttpResponse:
    """View for deleting jobs.

    Currently will only delete a job.
    """
    task = PeriodicTask.objects.filter(id=job_id).exclude(name="celery.backend_cleanup")

    if task.exists():
        task.first().delete()

    return redirect("/etl")


@never_cache
def job_schedule(request: HttpRequest) -> HttpResponse:
    """Get scheduled jobs."""
    context = {
        "scheduled_jobs": PeriodicTask.objects.filter(enabled=True),
    }

    return render(request, "etl/schedule.html.dj", context)
