"""ETL View functions."""
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django_celery_results.models import TaskResult


def solr_schedule():
    """Daily Solr update schedule."""
    return CrontabSchedule.objects.get_or_create(
        minute="30",
        hour="2",
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
    )[0]


def build_task_status(task_name, task_function):
    """Get task status."""
    task_status = {True: "success", False: "warning"}
    task = TaskResult.objects.filter(task_name=task_function)

    if not task.exists():
        return {"status": task_status[False], "message": "No run history."}

    # get last task status
    task_details = task.first().as_dict()
    periodic = PeriodicTask.objects.filter(task=task_function)

    status = "warning"

    if periodic.exists():
        status = task_status[periodic.first().enabled]

    return {
        "status": status,
        "message": "Last Status: %s; Last Run: %s"
        % (
            task_details["status"],
            timezone.datetime.strftime(task_details["date_done"], "%m/%d/%Y"),
        ),
    }


def toggle_task_status(task_name, task_function, arg):
    """Toggle a task status."""
    task = PeriodicTask.objects.get_or_create(
        crontab=solr_schedule(),
        name=task_name,
        task=task_function,
    )[0]

    task.enabled = bool(arg == "enable")
    task.save()

    return task.enabled
