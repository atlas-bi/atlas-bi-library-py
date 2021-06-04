from .settings import *
from .settings import BASE_DIR, INSTALLED_APPS

DEBUG = True

AUTHENTICATION_BACKENDS = ("atlas.no_pass_auth.Backend",)

LOGIN_URL = "/accounts/login/"

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


LOGIN_REDIRECT_URL = "/"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",  # for debug
    }
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
    "dg_db": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "atlas",
        "HOST": "postgres",
        "USER": "postgres",
        "PASSWORD": "",
    },
}

INSTALLED_APPS.append("debug_toolbar")
COMPRESS_ENABLED = False


# import custom overrides
try:
    from .dev_cust import *
except ImportError:
    pass
