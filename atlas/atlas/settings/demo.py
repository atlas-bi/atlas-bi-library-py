"""Atlas Demo Settings."""
import os
from urllib.parse import urlparse

import dj_database_url
import django_heroku

from .base import *

AUTHENTICATION_BACKENDS = ("atlas.no_pass_auth.Backend",)


LOGIN_URL = "/accounts/login/"

LOGIN_REDIRECT_URL = "/"

COMPRESS_ENABLED = True

DATABASES = {"default": dj_database_url.config(conn_max_age=600)}

# debug true as we run w/out a static file server (nginx.)
DEBUG = True
ALLOWED_HOSTS = ["*"]
DATABASE_ROUTERS: list = []  # type: ignore[no-redef]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",  # for debug
    }
}

parsed_redis_url = urlparse(REDIS_URL)  # noqa: F405


SESSION_REDIS = {
    "host": parsed_redis_url.hostname,
    "port": parsed_redis_url.port,
    "password": parsed_redis_url.password,
    "db": 0,
    "prefix": "atlas_session",
    "socket_timeout": 1,
    "retry_on_timeout": False,
}

CELERY_BROKER_URL = REDIS_URL  # noqa: F405

DEMO = True


class DisableMigrations:
    """Disable migrations to force a fresh db load."""

    def __contains__(self, item):
        """Return true for all keys."""
        return True

    def __getitem__(self, item):
        """Return none for all values."""
        return None


# pretend there are no migrations. By default the tests will create a database that is based
# on the latest migrations. Since we are not doing any migrations on the psql db (app is using
# mssql db in production/dev), we can ignore migrations for tests and just create a db based
# on the models.py file.
MIGRATION_MODULES = DisableMigrations()

django_heroku.settings(locals())
