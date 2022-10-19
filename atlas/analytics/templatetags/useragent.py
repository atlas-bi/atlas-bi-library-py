"""Custom template tag to render markdown."""
from django import template
from ua_parser import user_agent_parser

register = template.Library()


@register.simple_tag()
def agent_os(useragent: str) -> str:
    """Parse os useragent."""
    parsed = user_agent_parser.ParseOS(useragent)
    return (
        (parsed["family"] or "other")
        + " "
        + (parsed["major"] or "0")
        + "."
        + (parsed["minor"] or "0")
    )


@register.simple_tag()
def agent_browser(useragent: str) -> str:
    """Parse browser from useragent."""
    parsed = user_agent_parser.ParseUserAgent(useragent)
    return (parsed["family"] or "other") + " " + (parsed["major"] or "")
