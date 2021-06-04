import json

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render


def template(request):
    """Return search template.

    This view is public and requires no auth.
    """
    return render(None, "template.html")


@login_required
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

    permissions = request.user.get_permissions()
    user = request.user
    favorites = request.user.get_favorites()
    print(
        "%s%s?q=*%s*~"
        % (settings.SOLR_URL, search_type.replace("terms", "aterms"), search_string)
    )
    try:
        my_json = requests.get(
            "%s%s?q=*%s*~"
            % (settings.SOLR_URL, search_type.replace("terms", "aterms"), search_string)
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

    return JsonResponse(my_json, safe=False)


@login_required
def lookup(request, lookup):
    my_json = {}
    return JsonResponse(my_json, safe=False)
