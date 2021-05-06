import dj_database_url
import django_heroku

from .settings import *

AUTHENTICATION_BACKENDS = ("atlas.no_pass_auth.Backend",)

LOGIN_URL = "/accounts/login/"

LOGIN_REDIRECT_URL = "/"

COMPRESS_ENABLED = True

DATABASES = {}
DATABASES["default"] = dj_database_url.config(conn_max_age=600)


DEBUG = True
ALLOWED_HOSTS = ["*"]
DATABASE_ROUTERS: list = []

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",  # for debug
    }
}


class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


# pretend there are no migrations. By default the tests will create a database that is based
# on the latest migrations. Since we are not doing any migrations on the psql db (app is using
# mssql db in production/dev), we can ignore migrations for tests and just create a db based
# on the models.py file.
MIGRATION_MODULES = DisableMigrations()

django_heroku.settings(locals())
