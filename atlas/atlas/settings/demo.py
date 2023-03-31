"""Atlas Demo Settings."""

from typing import Any
from urllib.parse import urlparse

import dj_database_url

from .base import *

AUTHENTICATION_BACKENDS = ("atlas.no_pass_auth.Backend",)
ENABLE_LOGOUT = True

LOGIN_URL = "/accounts/login/"

LOGIN_REDIRECT_URL = "/"

COMPRESS_ENABLED = True

DEFAULT_DB = BASE_DIR / "db.sqlite"
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{DEFAULT_DB}", conn_max_age=600
    )
}

# use whitenoise for demo as we are not using nginx
DEBUG = False

MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")
# COMPRESS_ROOT = BASE_DIR / "static" / "CACHE"
COMPRESS_STORAGE = "compressor.storage.BrotliCompressorFileStorage"
# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
# WHITENOISE_MANIFEST_STRICT =False

ALLOWED_HOSTS = ["*"]
DATABASE_ROUTERS: list = []  # type: ignore[no-redef]

parsed_redis_url = urlparse(REDIS_URL)  # noqa: F405


SESSION_REDIS = {
    "host": parsed_redis_url.hostname or "",
    "port": str(parsed_redis_url.port or ""),
    "password": parsed_redis_url.password or "",
    "db": 0,
    "prefix": "atlas_session",
    "socket_timeout": 1,
    "retry_on_timeout": False,
}

CELERY_BROKER_URL = REDIS_URL  # noqa: F405
# COMPRESS_OFFLINE=True
DEMO = True


class DisableMigrations:
    """Disable migrations to force a fresh db load."""

    def __contains__(self, item: Any) -> bool:
        """Return true for all keys."""
        return True

    def __getitem__(self, item: Any) -> None:
        """Return none for all values."""
        return None


# pretend there are no migrations. By default the tests will create a database that is based
# on the latest migrations. Since we are not doing any migrations on the psql db (app is using
# mssql db in production/dev), we can ignore migrations for tests and just create a db based
# on the models.py file.
MIGRATION_MODULES = DisableMigrations()
