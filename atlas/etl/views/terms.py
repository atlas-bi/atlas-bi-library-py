"""Atlas ETL for Search."""
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache

from ..tasks.search.terms import reset_terms as task_reset_terms
from . import build_task_status, toggle_task_status


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
        return JsonResponse(
            {"message": toggle_task_status(task_name, task_function, arg)}
        )

    elif arg == "run":
        # Reload terms now.
        task_reset_terms.delay()

        return redirect("/etl")

    return JsonResponse({"status": "error"})
