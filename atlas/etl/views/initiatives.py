"""Atlas ETL for Search."""
import json
import logging

import pysolr
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django_celery_results.models import TaskResult

from atlas.celery import app as celery_app

from ..tasks.search.initiatives import reset_initiatives as task_reset_initiatives
from . import TASK_STATUS, solr_schedule


@never_cache
def initiatives(request, arg):
    """Search ETL for Initiatives.

    options:
        status: returns enabled/disabled status of ETL
        enable: enables the etl
        disable: disables the etl
        trigger: runs the etl
    """
    TASK_NAME = "search initiatives"
    TASK = "etl.tasks.search.initiatives.reset_initiatives"

    if arg == "status":
        task = (
            PeriodicTask.objects.filter(crontab=solr_schedule())
            .filter(name=TASK_NAME)
            .filter(task=TASK)
        )

        if task.exists():
            # get last task status

            task_details = (
                TaskResult.objects.filter(task_name=task.first().task).first().as_dict()
            )
            return JsonResponse(
                {
                    "status": TASK_STATUS[task.first().enabled],
                    "message": "Last Status: %s; Last Run: %s"
                    % (
                        task_details["status"],
                        timezone.datetime.strftime(
                            task_details["date_done"], "%m/%d/%Y"
                        ),
                    ),
                }
            )

        return JsonResponse(
            {"status": TASK_STATUS[False], "message": "No run history."}
        )

    elif arg in ["enable", "disable"]:
        task = PeriodicTask.objects.get_or_create(
            crontab=solr_schedule(),
            name=TASK_NAME,
            task=TASK,
        )[0]

        task.enabled = bool(arg == "enable")
        task.save()

        return JsonResponse({"message": task.enabled})

    elif arg == "run":
        """Reload initiatives now."""
        run = task_reset_initiatives.delay()

        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "error"})
