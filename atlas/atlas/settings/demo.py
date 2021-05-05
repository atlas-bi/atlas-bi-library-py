from .settings import *


AUTHENTICATION_BACKENDS = ("atlas.no_pass_auth.Backend",)

LOGIN_URL = "/accounts/login/"

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

DATABASE_ROUTERS: list = []