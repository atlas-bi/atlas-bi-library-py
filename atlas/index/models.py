from django.conf import settings as django_settings

if (
    hasattr(django_settings, "TESTING")
    and getattr(django_settings, "TESTING")
    or hasattr(django_settings, "DEMO")
    and getattr(django_settings, "DEMO")
):
    from index.models_psql import *
else:
    from index.models_sqlsvr import *
