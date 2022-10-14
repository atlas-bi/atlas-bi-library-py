"""Custom template tag to render markdown."""
from django import template

register = template.Library()


@register.filter(name="get_type")
def get_type(pathname):
    """Get page type from path."""
    if pathname.lower().startswith("/search"):
        return "Search"

    elif pathname.lower().startswith("/report"):
        return "Reports"
    elif pathname.lower().startswith("/initiative"):
        return "Initiatives"
    elif pathname.lower().startswith("/collection"):
        return "Collections"
    elif pathname.lower().startswith("/term"):
        return "Terms"
    elif pathname.lower().startswith("/group"):
        return "Groups"
    elif pathname.lower().startswith("/user"):
        return "Users"

    return "Other"
