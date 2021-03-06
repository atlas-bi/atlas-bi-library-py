"""Atlas ETL for Search."""

from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache

from ..tasks.search.initiatives import reset_initiatives as task_reset_initiatives
from . import build_task_status, toggle_task_status


@never_cache
def initiatives(request, arg):
    """Search ETL for Initiatives.

    options:
        status: returns enabled/disabled status of ETL
        enable: enables the etl
        disable: disables the etl
        trigger: runs the etl
    """
    task_name = "search initiatives"
    task_function = "etl.tasks.search.initiatives.reset_initiatives"

    if arg == "status":
        return JsonResponse(build_task_status(task_name, task_function))

    elif arg in ["enable", "disable"]:
        return JsonResponse(
            {"message": toggle_task_status(task_name, task_function, arg)}
        )

    elif arg == "run":
        # Reload initiatives now.
        task_reset_initiatives.delay()

        return redirect("/etl")

    return JsonResponse({"status": "error"})
