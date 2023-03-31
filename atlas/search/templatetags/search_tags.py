"""Custom template tags for search."""
import copy
from typing import Any, Dict
from urllib.parse import urlencode

from django import template

register = template.Library()


@register.filter(name="friendly_name")
def friendly_name(value: str) -> str:
    """Convert filter name to friendly name.

    :param value: input date
    :returns: string
    """
    cleaned = str(value).replace("_", " ").replace("text", "").strip()
    case_fixed = " ".join([w.title() if w.islower() else w for w in cleaned.split()])

    if case_fixed == "Y":
        return "Yes"
    elif case_fixed == "N":
        return "No"

    return case_fixed


@register.simple_tag(takes_context=True)
def facet_url(context: Dict[Any, Any], facet: str, value: str) -> str:
    """Convert filter name to friendly name.

    :param value: input date
    :returns: string
    """
    return (
        context.request.path  # type: ignore[attr-defined]
        + "?"
        + urlencode(set_parameter(context.request.GET, {facet: value}))  # type: ignore[attr-defined]
    )


@register.simple_tag(takes_context=True)
def facet_checked(context: Dict[Any, Any], facet: str, value: str) -> bool:
    """Convert filter name to friendly name.

    :param value: input date
    :returns: string
    """
    if context.request.GET.get(facet, None) == value:  # type: ignore[attr-defined]
        return True
    return False


@register.simple_tag(takes_context=True)
def facet_has_checked(context: Dict[Any, Any], facet: str) -> bool:
    """Convert filter name to friendly name.

    :param value: input date
    :returns: string
    """
    if context.request.GET.get(facet, None):  # type: ignore[attr-defined]
        return True
    return False


def set_parameter(query: Dict[Any, Any], parameters: Dict[Any, Any]) -> Dict[Any, Any]:
    """Set a query parameter."""
    query_copy = copy.deepcopy(query)

    if "type" in parameters:
        for key, _ in query.items():
            if (
                key != "type"
                and key != "query"
                and key != "advanced"
                and not (parameters["type"] == "reports" and key == "report_type_text")
            ):
                query_copy.pop(key)

        for key, value in parameters.items():
            if key in query and query[key] == value:
                query_copy.pop(key)
            else:
                query_copy[key] = value

    else:
        if "page" in query:
            query_copy.pop("page")

        for key, value in parameters.items():
            if key in query and value == query[key]:
                query_copy.pop(key)

            else:
                query_copy[key] = value

                if key == "report_type_text":
                    query_copy["type"] = "reports"

    return query_copy
