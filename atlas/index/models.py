from django.conf import settings as django_settings

if (hasattr(django_settings, "TESTING") and getattr(django_settings, "TESTING")
    or getattr(django_settings, "DATABASES")["default"]["ENGINE"] == "django.db.backends.postgresql"):
    from index.models_psql import *
else:
    from index.models_sqlsvr import *
