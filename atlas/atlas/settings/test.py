"""Atlas Settings for Test."""

import os

from selenium import webdriver

from .settings import *


class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


AUTHENTICATION_BACKENDS = ("atlas.no_pass_auth.Backend",)

LOGIN_URL = "/accounts/login/"

# docker run --name postgresql-container -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust -d postgres

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "atlas",
        "HOST": "localhost",
        "USER": "postgres",
        "PASSWORD": os.environ.get("PGPASSWORD", ""),
    },
}

TESTING = True
LOGIN_REDIRECT_URL = "/"

SESSION_REDIS = {
    "host": os.environ.get("REDIS_HOST", "localhost"),
    "port": 6379,
    "db": 0,
    "prefix": "atlas_session",
    "socket_timeout": 1,
    "retry_on_timeout": False,
}

SELENIUM_WEBDRIVERS = {
    "default": {
        "callable": webdriver.Chrome,
        "args": (),
        "kwargs": {},
    }
}

COMPRESS_ENABLED = False

DATABASE_ROUTERS: list = []

# pretend there are no migrations. By default the tests will create a database that is based
# on the latest migrations. Since we are not doing any migrations on the psql db (app is using
# mssql db in production/dev), we can ignore migrations for tests and just create a db based
# on the models.py file.
MIGRATION_MODULES = DisableMigrations()

# import custom overrides
try:
    from .test_cust import *
except ImportError:
    pass
