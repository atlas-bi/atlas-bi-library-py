"""Atlas dev settings."""
import contextlib

from .base import *
from .base import BASE_DIR, INSTALLED_APPS

DEBUG = True

AUTHENTICATION_BACKENDS = ("atlas.no_pass_auth.Backend",)  # type: ignore[assignment]
ENABLE_LOGOUT = True
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"

MIDDLEWARE = [
    "django.middleware.cache.UpdateCacheMiddleware",  # for caching
    "compression_middleware.middleware.CompressionMiddleware",
    "htmlmin.middleware.HtmlMinifyMiddleware",  # for htmlmin
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",  # for caching
    "htmlmin.middleware.MarkRequestMiddleware",  # for htmlmin
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",  # for debug
    }
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR / "db.sqlite3"),
    },
    "dg_db": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "atlas",
        "HOST": "postgres",
        "USER": "postgres",
        "PASSWORD": "",
    },
}

INSTALLED_APPS.insert(0, "django_gulp")
INSTALLED_APPS.append("debug_toolbar")

COMPRESS_ENABLED = False

GULP_DEVELOP_COMMAND = "gulp watch"
GULP_PRODUCTION_COMMAND = "gulp build"

# import custom overrides
with contextlib.suppress(ImportError):
    from .dev_cust import *
