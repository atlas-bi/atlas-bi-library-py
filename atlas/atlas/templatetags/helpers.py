"""Miscellaneous helper tags."""
from django import template

register = template.Library()


@register.filter(name="strip")
def strip_space(value):
    """Strip whitespace from string.

    :param value: string
    :returns: string
    """
    return str(value).strip()
