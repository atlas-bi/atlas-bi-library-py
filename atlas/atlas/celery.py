"""Celery Setup."""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "atlas.settings.prod")
app = Celery("atlas")

app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


# pylint: skip-file
# flake8: noqa
@app.task(bind=True)
def debug_task(self) -> None:  # type: ignore[no-untyped-def]
    print(f"Request: {self.request!r}")
