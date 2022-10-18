"""Atlas model loader."""
# pylint: disable=W0401, W0614
from django.conf import settings as django_settings

if getattr(django_settings, "TESTING", False) or getattr(
    django_settings, "DEMO", False
):
    from index.models_psql import *  # noqa: F401, F403
else:
    from index.models_sqlsvr import *  # noqa: F401, F403
