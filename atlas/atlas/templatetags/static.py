"""Miscellaneous helper tags."""
from compressor.filters.css_default import CssAbsoluteFilter
from django import template
from django.templatetags.static import StaticNode
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def static_hashed(path):
    """Return versioned static file.

    :param value: string
    :returns: string
    """
    return mark_safe(CssAbsoluteFilter(None).add_suffix(StaticNode.handle_simple(path)))
