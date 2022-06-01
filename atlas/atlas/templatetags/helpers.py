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
def snippet(model):
    """Create code snippet."""
    if model._meta.model.__name__ == "Reports":
        if model.has_docs() and model.docs.description:
            return (model.docs.description).strip()[:120] + "…"

        return (
            (model.description or "") + "\n" + (model.detailed_description or "")
        ).strip()[:120] + "…"

    if model._meta.model.__name__ == "Collections":
        return (model.search_summary or model.description or "").strip()[:120] + "…"

    if model._meta.model.__name__ == "Initiatives":
        return (model.description or "").strip()[:120] + "…"

    if model._meta.model.__name__ == "Terms":
        return (model.summary or model.technical_definition or "").strip()[:120] + "…"

    return "…"


@register.filter(name="possessive")
def possessive(value):
    """Add size to image url."""
    if value[-1].lower() == "s":
        return value + "'"
    return value + "'s"
