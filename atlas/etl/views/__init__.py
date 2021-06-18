from django_celery_beat.models import CrontabSchedule, PeriodicTask

task_status = {True: "success", False: "warning"}


def solr_schedule():
    """Daily Solr update schedule."""
    return CrontabSchedule.objects.get_or_create(
        minute="30",
        hour="2",
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
    )[0]
