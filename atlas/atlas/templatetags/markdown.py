"""Custom template tag to render markdown."""
import re

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
link_re = re.compile(r"^[^\]]https?:\/\/(.+)($|\/)")


def render_links(self, tokens, idx, options, env):
    print("here")
    token = tokens[idx]

    if link_re.match(token.attrs["src"]):

        ident = link_re.match(token.attrs["src"])[2]

        return '<a href={}">{}</a>'.format(
            ident,
            ident,
        )
    return self.links(tokens, idx, options, env)


@register.filter(name="markdown")
def markdown(value):
    """Convert value to markdown.

    :param value: input html
    :returns: markdown html
    """
    my_markdown = (
        MarkdownIt("commonmark")
        .enable("table")
        .use(tasklists_plugin, enabled=True)
        .use(footnote_plugin)
        .use(anchors_plugin)
        .use(texmath_plugin)
    )
    print("markdown")
    my_markdown.add_render_rule("links", render_links)

    return my_markdown.render(value)
