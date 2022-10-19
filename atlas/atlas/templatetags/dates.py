"""Custom template tags to render dates."""
from django import template
from RelativeToNow import relative_to_now

register = template.Library()


@register.filter(name="relative")
def relative(value: str) -> str:
    """Convert date to relative string.

    :param value: input date
    :returns: date string
    """
    return relative_to_now(value, no_error=True)
