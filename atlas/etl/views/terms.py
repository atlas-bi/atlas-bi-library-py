"""Atlas ETL for Search."""
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django_celery_beat.models import PeriodicTask

from ..tasks.search.terms import reset_terms as task_reset_terms
from . import build_task_status, solr_schedule


@never_cache
def terms(request, arg):
    """Search ETL for terms.

    options:
        status: returns enabled/disabled status of ETL
        enable: enables the etl
        disable: disables the etl
        trigger: runs the etl
    """
    task_name = "search terms"
    task_function = "etl.tasks.search.terms.reset_terms"

    if arg == "status":
        return JsonResponse(build_task_status(task_name, task_function))

    elif arg in ["enable", "disable"]:
        task = PeriodicTask.objects.get_or_create(
            crontab=solr_schedule(),
            name=task_name,
            task=task_function,
        )[0]

        task.enabled = bool(arg == "enable")
        task.save()

        return JsonResponse({"message": task.enabled})

    elif arg == "run":
        # Reload terms now.
        task_reset_terms.delay()

        return redirect("/etl")

    return JsonResponse({"status": "error"})
