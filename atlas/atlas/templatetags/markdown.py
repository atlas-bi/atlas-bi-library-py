"""Custom template tag to render markdown."""
from django import template
from markdown_it import MarkdownIt

register = template.Library()


@register.filter(name="markdown")
def markdown(value):
    """Convert value to markdown.

    :param value: input html
    :returns: markdown html
    """
    my_markdown = MarkdownIt().enable("table")

    return my_markdown.render(value)
