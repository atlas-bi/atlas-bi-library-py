"""Custom processer to enable access to settings in templates."""
from typing import Any, Dict
from urllib.parse import quote_plus

from django.conf import settings as django_settings
from django.http import HttpRequest
from index.models import ReportTypes


def user(request: HttpRequest) -> Dict[Any, Any]:
    """Context processor for user information."""
    if not request.user.is_anonymous:
        visible_reports = [
            quote_plus(x)
            for x in ReportTypes.objects.filter(visible="Y")
            .values_list("name", flat=True)
            .all()
        ]

        return {
            # "permissions": request.user.get_permissions(),
            "user": request.user,
            "favorites": request.user.get_starred_reports,
            "prefs": request.user.get_preferences,
            # needed to override the default django perms tag.
            "perms": request.user.get_all_permissions,
            # if we are in hyperspace. cookie is set in js.
            "is_hyperspace": bool(request.COOKIES.get("EPIC", False)),
            # network domain used to build ssrs urls
            "domain": getattr(
                django_settings,
                "DOMAIN",
                "example.com",
            ),
            "visible_reports": ("?report_type=" + "&report_type=".join(visible_reports))
            if visible_reports
            else "",
        }
    # context processor must ALWAYS return a dict
    return {}
