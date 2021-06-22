"""Custom template tag to render markdown."""
import re

import mdit_py_plugins
from django import template
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
def markdown(value):
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

    return my_markdown.render(value)
