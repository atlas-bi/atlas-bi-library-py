"""Atlas Search."""
import contextlib
import copy
import functools

import pysolr
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from index.models import Collections


@login_required
def template(request):
    """Return search template.

    This view is public and requires no auth.
    """
    return render(None, "template.html")


@never_cache
@login_required
def index(request, search_type="query", search_string=""):
    """Atlas Search.

    - search requests data from solr
    - get users permissions and favorites
    - modify json
        - add "favorite" column
        - add run url, based on permissions
        - adds collection ads

    Still need to add facet ranges

    """
    # if request.method == "GET":
    #     return render(request, "search.html.dj")

    request_dict = dict(request.GET)

    # create a solr instance, based on the search type.
    solr = pysolr.Solr(
        settings.SOLR_URL, search_handler=search_type.replace("terms", "aterms")
    )

    # pagination
    start = request_dict.get("start", [0])[0]

    # pylint: disable=C0301
    results = solr.search(
        build_search_string(search_string),
        fq=build_filter_query(request_dict),
        rq="{!rerank reRankQuery=$rqq reRankDocs=1000 reRankWeight=10}",
        rqq='(documented:1 OR executive_visibility_text:Y OR enabled_for_hyperspace_text:Y OR certification_text:"Analytics Certified")',  # noqa: E501
        start=start,
    )

    output = {
        "docs": results.docs,
        "facets": {},
        "hits": results.hits,
        "start": start,
        "search_filters": {**request_dict, **{"type": search_type or "query"}},
    }

    with contextlib.suppress(AttributeError):
        output["facets"] = copy.deepcopy(results.facets)

        for attr, _value in clean_dict(
            results.facets.get("facet_fields").items()
        ).items():
            fields = results.facets.get("facet_fields").get(attr)

            output["facets"]["facet_fields"][attr] = {
                field: fields[(num * 2) + 1] for num, field in enumerate(fields[::2])
            }

    # break early if collection, otherwise get collection ads.
    if search_type == "collections":
        return JsonResponse(output, safe=False)

    output["collections"] = build_collection_ads(results.docs)

    return JsonResponse(output, safe=False)


def clean_dict(my_dict):
    """Remove none values from dict."""
    return {attr: value for attr, value in my_dict if value}


def build_collection_ads(docs):
    """Build collection ad lists."""

    def get_item(doc, doc_type):
        """Get ids from list."""
        if doc.get("type")[0] == doc_type:
            return doc.get("atlas_id")[0]
        return None

    term_ids = filter(
        None, list(map(functools.partial(get_item, doc_type="terms"), docs))
    )
    report_ids = filter(
        None, list(map(functools.partial(get_item, doc_type="reports"), docs))
    )

    # get collections from results
    return list(
        Collections.objects.filter(
            Q(terms__term__term_id__in=term_ids)
            | Q(reports__report__report_id__in=report_ids)
        )
        .filter(Q(hidden__isnull=True) | Q(hidden="N"))
        .all()
        .values("collection_id", "search_summary", "name")
        .distinct()
    )


def build_search_string(search_string, search_type=None):
    """Escape invalid chars."""
    reserved_characters = (
        "\\",
        "+",
        "-",
        "&&",
        "||",
        "!",
        "(",
        ")",
        "{",
        "}",
        "[",
        "]",
        "^",
        '"',
        "~",
        "*",
        "?",
        ":",
        "/",
    )

    if search_string is None:
        return "*"

    def build_fuzzy(sub_str):
        """Add fuzzy option."""
        if len(sub_str) > 1:
            fuzy_type = "~" if sub_str is None else "*~"
            return sub_str + fuzy_type + str(max(len(sub_str) // 3, 1))

        elif len(sub_str) == 1:
            return sub_str + "*~"

        return sub_str

    # clean search string
    for char in reserved_characters:
        search_string = search_string.replace(char, "\\%s" % char)

    # change search terms to fuzzy.. allow changing up to 1/2 the word
    search_string_fuzzy = " ".join(
        build_fuzzy(item) for item in search_string.split(" ")
    )

    return "name:({search})^6 OR name:({fuzzy})^3 OR ({search})^5 OR ({fuzzy})".format(
        search=search_string, fuzzy=search_string_fuzzy
    )


def build_filter_query(request_dict):
    """Build filter query from items."""
    if not request_dict:
        return request_dict

    filter_query = []

    # add visibility filter - by default only showing visible reports
    if request_dict.get("visibility_text", "Y") == ["Y"]:
        filter_query.append("{!tag=visibility_text}visibility_text:Y")
    else:
        filter_query.append(
            "{!tag=visibility_text}visibility_text:Y OR {!tag=visibility_text}visibility_text:N"
        )

    request_dict = request_dict.pop("visibility_text")
    request_dict = request_dict.pop("start")

    for key, values in request_dict.items():
        # it is possible to have multiple filters
        # per field
        filter_query.append(
            "%s"
            % " OR ".join(
                "{!tag=%s}%s:%s"
                % (
                    key,
                    key,
                    value,
                )
                for value in values
            )
        )

    return ",".join(filter_query)


@never_cache
@login_required
def user_lookup(request, role=None):
    """User lookup."""
    solr = pysolr.Solr(settings.SOLR_URL, search_handler="users")

    results = solr.search(
        build_search_string(request.GET.get("s"), search_type="fuzzy"),
        fq=("user_roles:%s" % role if role else "*:*"),
        **{"rows": 20}
    )

    output = [
        {"ObjectId": item.get("atlas_id"), "Name": item.get("name")} for item in results
    ]
    return JsonResponse(output, safe=False)


@never_cache
@login_required
def collection_lookup(request):
    """Dropdown lookup for collections."""
    search_string = build_search_string(request.GET.get("s"), search_type="fuzzy")

    solr = pysolr.Solr(settings.SOLR_URL, search_handler="collections")

    results = solr.search(build_search_string(search_string), **{"rows": 20})

    output = [
        {"ObjectId": item.get("atlas_id"), "Name": item.get("name")} for item in results
    ]
    return JsonResponse(output, safe=False)


@never_cache
@login_required
def report_lookup(request):
    """Report lookup."""
    search_string = build_search_string(request.GET.get("s"), search_type="fuzzy")

    solr = pysolr.Solr(settings.SOLR_URL, search_handler="reports")

    results = solr.search(build_search_string(search_string), **{"rows": 20})

    output = [
        {"ObjectId": item.get("atlas_id"), "Name": item.get("name")} for item in results
    ]
    return JsonResponse(output, safe=False)


@never_cache
@login_required
def term_lookup(request):
    """Term lookup."""
    search_string = build_search_string(request.GET.get("s"), search_type="fuzzy")

    solr = pysolr.Solr(settings.SOLR_URL, search_handler="aterms")

    results = solr.search(build_search_string(search_string), **{"rows": 20})

    output = [
        {"ObjectId": item.get("atlas_id"), "Name": item.get("name")} for item in results
    ]
    return JsonResponse(output, safe=False)


@never_cache
@login_required
def dropdown_lookup(request, lookup):
    """Mini search for dropdowns."""
    solr = pysolr.Solr(settings.SOLR_LOOKUP_URL)

    lookup_values = [
        {"ObjectId": value.get("atlas_id"), "Name": value.get("item_name")}
        for value in solr.search("item_type:%s" % lookup, **{"rows": 9999})
    ]

    return JsonResponse(lookup_values, safe=False)
