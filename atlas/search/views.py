import json

import requests
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.


@login_required
def index(request, search_string=None):

    context = {
        "permissions": request.user.get_permissions(),
        "user": request.user,
        "favorites": request.user.get_favorites(),
    }

    return render(request, "search.html.dj", context)


def template(request):
    """Return search template.

    This view is public and requires no auth.
    """
    return render(None, "template.html")


@login_required
def search(request, search_string):
    """Atlas Search.

    - search requests data from solr
    - get users permissions and favorites
    - modify json
        - add "favorite" column
        - add run url, based on permissions

    """

    permissions = request.user.get_permissions()
    user = request.user
    favorites = request.user.get_favorites()

    search_type = request.GET.get("type", default="query")

    my_json = requests.get(
        "http://solr.riversidehealthcare.net:8983/solr/atlas/%s?q=*%s*~"
        % (search_type, search_string)
    ).json()

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

    return JsonResponse(my_json, safe=False)
