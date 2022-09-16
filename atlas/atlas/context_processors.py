"""Custom processer to enable access to settings in templates."""
from django.conf import settings as django_settings


# https://stackoverflow.com/a/53953578/10265880
def settings(request):
    """Return setting value... if allowed."""
    settings_in_templates = {}
    for attr in [
        "ORG_NAME",
        "LOGIN_TITLE",
        "DEMO",
        "FOOTER_SUBTITLE",
    ]:  # Write here the settings you want to expose to the templates.
        if hasattr(django_settings, attr):
            settings_in_templates[attr] = getattr(django_settings, attr)
    return {
        "settings": settings_in_templates,
    }


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
            "is_hyperspace": bool(request.COOKIES.get('EPIC',False)),
            # network domain used to build ssrs urls
            "domain": getattr(django_settings, "DOMAIN") if hasattr(django_settings, "DOMAIN") else "example.com"

        }
    # context processor must ALWAYS return a dict
    return {}
