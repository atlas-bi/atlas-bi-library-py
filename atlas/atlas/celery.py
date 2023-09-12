"""Celery Setup."""
from celery import Celery

app = Celery("atlas")

app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


# pylint: skip-file
# flake8: noqa
@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
