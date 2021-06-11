import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "atlas.settings.dev")

from celery import Celery

app = Celery("atlas")

app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
