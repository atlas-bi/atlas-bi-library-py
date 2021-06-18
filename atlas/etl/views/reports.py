"""Atlas ETL for Search."""
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django_celery_beat.models import PeriodicTask
from django_celery_results.models import TaskResult

from ..tasks.search.reports import reset_reports as task_reset_reports
from . import solr_schedule, task_status


@never_cache
def reports(request, arg):
    """Search ETL for reports.

    options:
        status: returns enabled/disabled status of ETL
        enable: enables the etl
        disable: disables the etl
        trigger: runs the etl
    """
    task_name = "search reports"
    task_function = "etl.tasks.search.reports.reset_reports"

    if arg == "status":
        task = TaskResult.objects.filter(task_name=task_function)

        if task.exists():
            # get last task status

            task_details = task.first().as_dict()
            periodic = PeriodicTask.objects.filter(task=task_function)

            status = (
                task_status[periodic.first().enabled]
                if periodic.exists()
                else "warning"
            )
            return JsonResponse(
                {
                    "status": status,
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
            {"status": task_status[False], "message": "No run history."}
        )

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
        """Reload reports now."""
        task_reset_reports.delay()

        return redirect("/etl")

    return JsonResponse({"status": "error"})
