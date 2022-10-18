"""Atlas ETL for Search."""
# pylint: disable=W0613
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache

from ..tasks.search.reports import reset_reports as task_reset_reports
from . import build_task_status, toggle_task_status


@never_cache
def reports(request: HttpRequest, arg: str) -> JsonResponse:
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
        return JsonResponse(build_task_status(task_name, task_function))
    if arg in ["enable", "disable"]:
        return JsonResponse(
            {"message": toggle_task_status(task_name, task_function, arg)}
        )

    if arg == "run":
        # Reload reports now.
        task_reset_reports.delay()

        return redirect("/etl")

    return JsonResponse({"status": "error"})
