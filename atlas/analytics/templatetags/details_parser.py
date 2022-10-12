"""Custom template tag to render markdown."""

import json

from django import template

register = template.Library()


def dict_key_unspacer(dictionary):
    """Remove space from dictionary key names.

    https://stackoverflow.com/a/48353438/10265880
    """
    new = {}
    for key, value in dictionary.items():
        if isinstance(value, dict):
            value = dict_key_unspacer(value)
        new[key.replace(" ", "_")] = value
    return new


@register.simple_tag()
def details_parser(details):
    """Parse os useragent."""
    return dict_key_unspacer(json.loads(details))


@register.filter(name="severity")
def severity(code):
    """Convert severity code to some nice text."""
    levels = {
        1000: "😊 Trace",
        2000: "🙂 Debug",
        3000: "😐 Info",
        4000: "😨 Warning",
        5000: "😠 Error",
        6000: "😡 Fatal",
    }
    return levels.get(code, "🙂 Debug")
