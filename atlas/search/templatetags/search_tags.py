"""Custom template tags to render dates."""
import copy
from urllib.parse import urlencode

from django import template
from RelativeToNow import relative_to_now

register = template.Library()


@register.filter(name="friendly_name")
def friendly_name(value):
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
def facet_url(context, facet, value):
    """Convert filter name to friendly name.

    :param value: input date
    :returns: string
    """
    return (
        context.request.path
        + "?"
        + urlencode(set_parameter(context.request.GET, {facet: value}))
    )


@register.simple_tag(takes_context=True)
def facet_checked(context, facet, value):
    """Convert filter name to friendly name.

    :param value: input date
    :returns: string
    """
    if context.request.GET.get(facet, None) == value:
        return True
    return False


@register.simple_tag(takes_context=True)
def facet_has_checked(context, facet):
    """Convert filter name to friendly name.

    :param value: input date
    :returns: string
    """
    if context.request.GET.get(facet, None):
        return True
    return False


def set_parameter(query, parameters):
    query_copy = copy.deepcopy(query)

    if "type" in parameters:
        for key, value in query.items():
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


#             var qs = QueryHelpers.ParseQuery(helper.Request.QueryString.Value ?? "");
#             // if we are changing type, we should remove all other filters.
#             if (parameters.ContainsKey("type"))
#                 foreach (var p in qs)
#                     if (
#                         p.Key != "type"
#                         && p.Key != "Query"
#                         && p.Key != "advanced"
#                         && !(parameters["type"] == "reports" && p.Key == "report_type_text")
#                     )
#                         qs.Remove(p.Key);
#                 foreach (var p in parameters)
#                     // if we need an "uncheck" url, the pop the key.
#                     if (qs.ContainsKey(p.Key) && qs[p.Key] == p.Value)
#                         qs.Remove(p.Key);
#                     else
#                         qs[p.Key] = p.Value;
#             else
#             {
#                 foreach (var p in parameters)
#                 {
#                     // remove change page from query
#                     if (qs.ContainsKey("PageIndex"))
#                     {
#                         qs.Remove("PageIndex");
#                     }
#                     // if we need an "uncheck" url, the pop the key.
#                     if (qs.ContainsKey(p.Key) && qs[p.Key] == p.Value)
#                     {
#                         qs.Remove(p.Key);
#                     }
#                     else
#                     {
#                         qs[p.Key] = p.Value;
#                         if (p.Key == "report_type_text")
#                         {
#                             qs["type"] = "reports";
#                         }
#                     }
#                 }
#             }
#             return helper.Request.Path + QueryString.Create(qs);
#         }
