"""Custom template tag to render markdown."""
import re

import bleach
from bs4 import BeautifulSoup
from django import template
from django.conf import settings as django_settings
from django.utils.safestring import mark_safe
from markdown_it import MarkdownIt
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.tasklists import tasklists_plugin
from mdit_py_plugins.texmath import texmath_plugin

register = template.Library()

"""
To do:

    * convert epic identifiers to record viewer links
    * flow charts

"""


@register.filter(name="markdown")
def markdown(value: str) -> str:
    """Convert value to markdown.

    :param value: input html
    :returns: markdown html
    """
    my_markdown = (
        MarkdownIt("gfm-like", {"breaks": True})
        .enable(["table", "replacements", "smartquotes", "linkify"])
        .use(tasklists_plugin, enabled=True)
        .use(footnote_plugin)
        .use(anchors_plugin)
        .use(texmath_plugin)
    )

    return mark_safe(
        bleach.clean(my_markdown.render(value), tags=django_settings.SAFE_HTML_TAGS)
    )


@register.filter(name="unwrap")
def unwrap(html: str) -> str:
    """Remove outer <p></p> tag from html."""
    return re.sub(r"^<p>|</p>$", "", html)


@register.filter(name="text")
def text(html: str) -> str:
    """Get text from html."""
    soup = BeautifulSoup(html, "html5lib")
    return soup.get_text()
