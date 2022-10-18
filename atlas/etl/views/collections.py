"""Atlas ETL for Search."""
# pylint: disable=W0613
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache

from ..tasks.search.collections import reset_collections as task_reset_collections
from . import build_task_status, toggle_task_status


@never_cache
def collections(request: HttpRequest, arg: str) -> JsonResponse:
    """Search ETL for collections.

    options:
        status: returns enabled/disabled status of ETL
        enable: enables the etl
        disable: disables the etl
        trigger: runs the etl
    """
    task_name = "search collections"
    task_function = "etl.tasks.search.collections.reset_collections"

    if arg == "status":
        return JsonResponse(build_task_status(task_name, task_function))
    if arg in ["enable", "disable"]:
        return JsonResponse(
            {"message": toggle_task_status(task_name, task_function, arg)}
        )

    if arg == "run":
        # Reload collections now.
        task_reset_collections.delay()

        return redirect("/etl")

    return JsonResponse({"status": "error"})
