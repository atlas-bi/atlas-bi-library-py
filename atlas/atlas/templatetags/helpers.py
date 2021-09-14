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


@register.filter(name="risk_level")
def risk_level(value):
    """Convert cert tag to color code.

    :param value: cert tag
    :returns: css class
    """
    lookup = {
        "Analytics Certified": "is-success",
        "Analytics Reviewed": "is-info",
        "Epic Released": "is-warning",
        "Legacy": "is-warning",
        "High Risk": "is-danger",
    }

    return lookup.get(value, "")


@register.filter(name="size")
def size(value, arg):
    """Add size to image url."""
    return value + "?size=" + arg


@register.filter(name="snippet")
def snippet(report):

    if report.has_docs() and report.docs.description:
        return (report.docs.description).strip()[:120] + "…"

    return (
        (report.description or "") + "\n" + (report.detailed_description or "")
    ).strip()[:120] + "…"
