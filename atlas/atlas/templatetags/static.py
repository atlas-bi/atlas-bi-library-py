"""Miscellaneous helper tags."""
from compressor.filters.css_default import CssAbsoluteFilter
from django import template
from django.templatetags.static import StaticNode
from django.utils.safestring import mark_safe
from index.models import GlobalSettings

register = template.Library()


@register.simple_tag
def static_hashed(path):
    """Return versioned static file.

    :param value: string
    :returns: string
    """
    return mark_safe(CssAbsoluteFilter(None).add_suffix(StaticNode.handle_simple(path)))


@register.simple_tag
def global_css():
    """Return global css overrides.

    :returns: string
    """
    global_css = GlobalSettings.objects.filter(name="global_css").first()
    if global_css:
        return mark_safe(f"<style>{global_css.value}</style>")
    return ""
