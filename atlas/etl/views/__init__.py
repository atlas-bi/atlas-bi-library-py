"""ETL View functions."""
from typing import Any, Dict

from django.db import models
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django_celery_results.models import TaskResult


def solr_schedule() -> models.Model:
    """Daily Solr update schedule."""
    return CrontabSchedule.objects.get_or_create(
        minute="30",
        hour="2",
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
    )[0]


def build_task_status(task_name: str, task_function: str) -> Dict[str, Any]:
    """Get task status."""
    task_status = {
        "SUCCESS": "success",
        "STARTED": "warning",
        "FAILURE": "error",
        "NONE": "warning",
    }
    task = TaskResult.objects.filter(task_name=task_function)

    if not task.exists():
        return {
            "status": task_status["NONE"],
            "active": build_task_active(task_name, task_function),
            "message": "No run history.",
        }

    # get last task status
    task_details = task.first().as_dict()

    return {
        "status": task_status[task_details.get("status", "NONE")],
        "active": build_task_active(task_name, task_function),
        "message": "Last Status: %s; Last Run: %s"
        % (
            task_details["status"],
            timezone.datetime.strftime(task_details["date_done"], "%m/%d/%Y"),
        ),
    }


def build_task_active(task_name: str, task_function: str) -> bool:
    """Get task status."""
    task = PeriodicTask.objects.filter(
        name=task_name,
        task=task_function,
    )
    if task.exists():
        return task.first().enabled

    return False


def toggle_task_status(task_name: str, task_function: str, arg: str) -> bool:
    """Toggle a task status."""
    task = PeriodicTask.objects.get_or_create(
        crontab=solr_schedule(),
        name=task_name,
        task=task_function,
    )[0]

    task.enabled = bool(arg == "enable")
    task.save()

    return task.enabled
