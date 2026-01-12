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

DEBUG = environ.get("DEBUG", "") == "1"

allowed_hosts_env = environ.get("ALLOWED_HOSTS", "localhost,api")
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(",") if host.strip()]

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
DB_MODE = environ.get("DB_MODE", "dual").strip().lower()
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
    driver = environ.get("SQLSERVER_DRIVER", "ODBC Driver 17 for SQL Server")
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
# Staticfiles
######################################################################
STATIC_URL = "static/"

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
    "SITE_HEADER": _("Turbo Admin"),
    "SITE_TITLE": _("Turbo Admin"),
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
