"""Custom template tag to render markdown."""
from django import template

register = template.Library()


@register.filter(name="get_type")
def get_type(pathname: str) -> str:
    """Get page type from path."""
    if pathname.lower().startswith("/search"):
        return "Search"

    if pathname.lower().startswith("/report"):
        return "Reports"
    if pathname.lower().startswith("/initiative"):
        return "Initiatives"
    if pathname.lower().startswith("/collection"):
        return "Collections"
    if pathname.lower().startswith("/term"):
        return "Terms"
    if pathname.lower().startswith("/group"):
        return "Groups"
    if pathname.lower().startswith("/user"):
        return "Users"

    return "Other"
