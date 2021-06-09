import json

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


def template(request):
    """Return search template.

    This view is public and requires no auth.
    """
    return render(None, "template.html")


# @login_required
@csrf_exempt
def index(request, search_type="query", search_string=""):
    """Atlas Search.

    - search requests data from solr
    - get users permissions and favorites
    - modify json
        - add "favorite" column
        - add run url, based on permissions

    """

    if request.method == "GET":
        context = {
            "permissions": request.user.get_permissions(),
            "user": request.user,
            "favorites": request.user.get_favorites(),
        }

        return render(request, "search.html.dj", context)

    # permissions = request.user.get_permissions()
    # user = request.user
    # favorites = request.user.get_favorites()
    search_filters = ""
    for key, values in dict(request.GET).items():
        # it is possible to have multiple filters
        # per field
        if key != "visibility_text" and key != "start":
            search_filters += "&fq=%s" % " OR ".join(
                '{!tag=%s}%s:"%s"'
                % (
                    key,
                    key,
                    value,
                )
                for value in values
            )
    print(search_filters)
    # if we are searching reports and did not explicitly add "visibility_text:N" then add "visibility_text:Y"

    if "visibility_text" not in dict(request.GET) or dict(request.GET).get(
        "visibility_text"
    ) == ["Y"]:
        search_filters += "&fq=({!tag=visibility_text}visibility_text:Y)"
    else:
        search_filters += "&fq=({!tag=visibility_text}visibility_text:Y OR {!tag=visibility_text}visibility_text:N)"

    # pagination
    if "start" in dict(request.GET):
        search_filters += "&start=%s" % dict(request.GET).get("start")[0]

    try:
        my_json = requests.get(
            '%s%s?q=(name:"%s"^4 OR name:"*%s*~"^3 OR "%s"^2 OR "*%s*~")%s&rq={!rerank reRankQuery=$rqq reRankDocs=1000 reRankWeight=10}&rqq=(documented:1 OR executive_visibility_text:Y OR enabled_for_hyperspace_text:Y OR certification_text:"Analytics Certified")'
            % (
                settings.SOLR_URL,
                search_type.replace("terms", "aterms"),
                search_string,
                search_string,
                search_string,
                search_string,
                search_filters,
            )
        ).json()
    except:
        my_json = {}

    if my_json.get("facet_counts"):
        for attr, value in my_json.get("facet_counts").items():
            if value:
                for sub_attr, sub_value in (
                    my_json.get("facet_counts").get(attr).items()
                ):
                    if isinstance(sub_value, list):
                        my_json.get("facet_counts").get(attr)[sub_attr] = dict(
                            zip(sub_value[::2], sub_value[1::2])
                        )

    # pass back search filters
    my_json["search_filters"] = {"type": search_type or "query"}

    for key, values in dict(request.GET).items():
        my_json["search_filters"][key] = values

    print(my_json["search_filters"])
    return JsonResponse(my_json, safe=False)


@login_required
def lookup(request, lookup):
    my_json = {}
    return JsonResponse(my_json, safe=False)
