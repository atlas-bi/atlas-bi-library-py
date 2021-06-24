"""Atlas ETL for Search."""
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache

from ..tasks.search.projects import reset_projects as task_reset_projects
from . import build_task_status, toggle_task_status


@never_cache
def projects(request, arg):
    """Search ETL for projects.

    options:
        status: returns enabled/disabled status of ETL
        enable: enables the etl
        disable: disables the etl
        trigger: runs the etl
    """
    task_name = "search projects"
    task_function = "etl.tasks.search.projects.reset_projects"

    if arg == "status":
        return JsonResponse(build_task_status(task_name, task_function))

    elif arg in ["enable", "disable"]:
        return JsonResponse(
            {"message": toggle_task_status(task_name, task_function, arg)}
        )

    elif arg == "run":
        # Reload projects now.
        task_reset_projects.delay()

        return redirect("/etl")

    return JsonResponse({"status": "error"})
