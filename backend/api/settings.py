from os import environ
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

######################################################################
# General
######################################################################
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = environ.get("SECRET_KEY", get_random_secret_key())

DEBUG = environ.get("DEBUG", "1") != "0"

allowed_hosts_env = environ.get("ALLOWED_HOSTS", "localhost,api")
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(",") if host.strip()]

csrf_trusted_origins_env = environ.get("CSRF_TRUSTED_ORIGINS", "").strip()
if csrf_trusted_origins_env:
    CSRF_TRUSTED_ORIGINS = [
        origin.strip()
        for origin in csrf_trusted_origins_env.split(",")
        if origin.strip()
    ]

WSGI_APPLICATION = "api.wsgi.application"

ROOT_URLCONF = "api.urls"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

######################################################################
# Apps
######################################################################
INSTALLED_APPS = [
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_celery_results",
    "django_celery_beat",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "api",
    "atlas_index",
]

######################################################################
# Middleware
######################################################################
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


def _env_bool(name: str, default: bool = False) -> bool:
    val = environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "y", "on"}


if _env_bool("USE_WHITENOISE", False):
    if "whitenoise.middleware.WhiteNoiseMiddleware" not in MIDDLEWARE:
        try:
            idx = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
            MIDDLEWARE.insert(idx + 1, "whitenoise.middleware.WhiteNoiseMiddleware")
        except ValueError:
            MIDDLEWARE.insert(0, "whitenoise.middleware.WhiteNoiseMiddleware")

if _env_bool("USE_X_FORWARDED_HOST", False):
    USE_X_FORWARDED_HOST = True

if _env_bool("USE_X_FORWARDED_PORT", False):
    USE_X_FORWARDED_PORT = True

if _env_bool("SECURE_PROXY_SSL_HEADER", False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if _env_bool("CSRF_COOKIE_SECURE", False):
    CSRF_COOKIE_SECURE = True

if _env_bool("SESSION_COOKIE_SECURE", False):
    SESSION_COOKIE_SECURE = True

######################################################################
# Templates
######################################################################
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

######################################################################
# Database
######################################################################
_is_pytest = "PYTEST_CURRENT_TEST" in environ
DB_MODE = environ.get("DB_MODE", "single" if _is_pytest else "dual").strip().lower()
DEFAULT_DB_VENDOR = environ.get("DEFAULT_DB_VENDOR", "postgres").strip().lower()


def _postgres_db(prefix: str = "DATABASE_") -> dict:
    return {
        "ENGINE": "django.db.backends.postgresql",
        "USER": environ.get(f"{prefix}USER", "postgres"),
        "PASSWORD": environ.get(f"{prefix}PASSWORD", "change-password"),
        "NAME": environ.get(f"{prefix}NAME", "db"),
        "HOST": environ.get(f"{prefix}HOST", "localhost"),
        "PORT": environ.get(f"{prefix}PORT", "5432"),
        "TEST": {
            "NAME": environ.get(f"{prefix}TEST_NAME", "test"),
        },
    }


def _sqlserver_db(prefix: str = "DATABASE_") -> dict:
    driver = environ.get("SQLSERVER_DRIVER", "ODBC Driver 18 for SQL Server")
    extra_params = environ.get("SQLSERVER_EXTRA_PARAMS", "MARS_Connection=Yes")
    return {
        "ENGINE": "mssql",
        "NAME": environ.get(f"{prefix}NAME", "atlas"),
        "HOST": environ.get(f"{prefix}HOST", "localhost"),
        "USER": environ.get(f"{prefix}USER", "sa"),
        "PASSWORD": environ.get(f"{prefix}PASSWORD", ""),
        "PORT": environ.get(f"{prefix}PORT", "1433"),
        "OPTIONS": {
            "driver": driver,
            "extra_params": extra_params,
        },
    }


def _db_for(vendor: str, prefix: str = "DATABASE_") -> dict:
    vendor = vendor.strip().lower()
    if vendor in {"postgres", "postgresql", "psql"}:
        return _postgres_db(prefix=prefix)
    if vendor in {"mssql", "sqlserver", "sql_server"}:
        return _sqlserver_db(prefix=prefix)
    raise ValueError(
        f"Unsupported DB vendor: {vendor!r}. Use postgres or mssql (sqlserver)."
    )


DATABASES = {
    "default": _db_for(DEFAULT_DB_VENDOR, prefix="DATABASE_"),
}

DATABASE_ROUTERS: list[str] = []

if DB_MODE == "dual":
    DG_DB_VENDOR = environ.get("DG_DB_VENDOR", "mssql").strip().lower()
    DATABASES["dg_db"] = _db_for(DG_DB_VENDOR, prefix="DG_DB_")
    DATABASE_ROUTERS = ["api.db_routers.DgDbRouter"]

######################################################################
# Authentication
######################################################################
AUTH_USER_MODEL = "api.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

######################################################################
# Internationalization
######################################################################
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

######################################################################
# Celery
######################################################################
REDIS_URL = environ.get("REDIS_URL", "redis://127.0.0.1:6379").strip()

CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_URL = environ.get("CELERY_BROKER_URL", REDIS_URL).strip()
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
DJANGO_CELERY_BEAT_TZ_AWARE = True
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_RESULT_EXTENDED = True

######################################################################
# Staticfiles
######################################################################
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

if _env_bool("USE_WHITENOISE", False):
    STATICFILES_STORAGE = environ.get(
        "STATICFILES_STORAGE",
        "whitenoise.storage.CompressedManifestStaticFilesStorage",
    )

######################################################################
# Solr
######################################################################
SOLR_URL = environ.get("SOLR_URL", "").strip()
SOLR_LOOKUP_URL = environ.get("SOLR_LOOKUP_URL", "").strip()

######################################################################
# Rest Framework
######################################################################
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
}

######################################################################
# Unfold
######################################################################
UNFOLD = {
    "SITE_HEADER": _("Atlas Admin"),
    "SITE_TITLE": _("Atlas Admin"),
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Navigation"),
                "separator": False,
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "person",
                        "link": reverse_lazy("admin:api_user_changelist"),
                    },
                    {
                        "title": _("Groups"),
                        "icon": "label",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        ],
    },
}
