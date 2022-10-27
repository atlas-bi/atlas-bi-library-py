"""Miscellaneous helper tags."""
from django import template
from django.db.models import Model

register = template.Library()


@register.filter(name="strip")
def strip_space(value: str) -> str:
    """Strip whitespace from string.

    :param value: string
    :returns: string
    """
    return str(value).strip()


@register.filter(name="remove_slash")
def remove_slash(value: str) -> str:
    """Strip whitespace from string.

    :param value: string
    :returns: string
    """
    return value[:1] if value[-1] == "/" else value


@register.filter(name="size")
def size(value: str, arg: str) -> str:
    """Add size to image url."""
    return value + "?size=" + arg


@register.filter(name="snippet")
def snippet(model: Model) -> str:
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
def possessive(value: str) -> str:
    """Add size to image url."""
    if value[-1].lower() == "s":
        return value + "'"
    return value + "'s"
