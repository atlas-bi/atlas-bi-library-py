from .settings import *


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

COMPRESS_ENABLED = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "atlas",
        "HOST": "127.0.0.1",
        "USER": "atlas",
        "PASSWORD": "12345",
    },
}