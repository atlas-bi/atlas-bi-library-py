"""Atlas ETL for Dropdown lookups."""
# pylint: disable=W0613
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache

from ..tasks.search.lookups import reset_lookups as task_reset_lookups
from . import build_task_status, toggle_task_status


@never_cache
def lookups(request: HttpRequest, arg: str) -> JsonResponse:
    """Search ETL for lookups.

    options:
        status: returns enabled/disabled status of ETL
        enable: enables the etl
        disable: disables the etl
        trigger: runs the etl
    """
    task_name = "search lookups"
    task_function = "etl.tasks.search.lookups.reset_lookups"

    if arg == "status":
        return JsonResponse(build_task_status(task_name, task_function))

    if arg in ["enable", "disable"]:
        return JsonResponse(
            {"message": toggle_task_status(task_name, task_function, arg)}
        )

    if arg == "run":
        # Reload lookups now.
        task_reset_lookups.delay()

        return redirect("/etl")

    return JsonResponse({"status": "error"})
