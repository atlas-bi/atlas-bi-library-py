from .settings import *

BASE_DIR = Path(__file__).resolve().parent.parent.parent
AUTHENTICATION_BACKENDS = ("atlas.no_pass_auth.Backend",)

LOGIN_URL = "/accounts/login/"

LOGIN_REDIRECT_URL = "/"

COMPRESS_ENABLED = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / "db.sqlite3",
    }
}

DEBUG=True
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