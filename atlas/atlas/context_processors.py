"""Custom processer to enable access to settings in templates."""
from django.conf import settings as django_settings


def user(request):
    """Context processor for user information."""
    if not request.user.is_anonymous:
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
        }
    # context processor must ALWAYS return a dict
    return {}
