"""Custom template tag to render markdown."""
from django import template

register = template.Library()


@register.filter(name="authorized")
def authorized(value):
    """Check if user is authorized to use favorites.

    :param value: list of permissions
    :returns: true/false if they have a 41
    """
    if value:
        return 41 in value
    return False
