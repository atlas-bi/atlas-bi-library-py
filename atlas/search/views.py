"""Atlas Search."""
# pylint: disable=R0914, R0915, W0613
import contextlib
import copy
import math
import re
from typing import Any, Dict, List, Optional

import pysolr
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from index.models import (
    Collections,
    Groups,
    Initiatives,
    ReportImages,
    Reports,
    Terms,
    Users,
)

from atlas.decorators import NeverCacheMixin


class Index(NeverCacheMixin, LoginRequiredMixin, TemplateView):
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

    def get_template_names(self) -> List[str]:
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return ["search/ajax.html.dj"]
        return ["search/index.html.dj"]

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        context = super().get_context_data(**kwargs)
        search_type = self.request.GET.get("type", "query")
        search_string = self.request.GET.get("query")
        request_dict = dict(self.request.GET)
        page = max(int(request_dict.get("page", [1])[0]), 1)
        max_results = 20
        page_slide = 2

        def build_filter_fields(search_type: str) -> Optional[List[Dict[str, str]]]:
            if search_type == "reports":
                return [
                    {"key": "name", "value": "Name"},
                    {"key": "description", "value": "Description"},
                    {"key": "query", "value": "Query"},
                    {"key": "epic_record_id", "value": "Epic ID"},
                    {"key": "epic_template", "value": "Epic Template ID"},
                ]
            return None

        def build_filter_list(request_dict: Dict[Any, Any]) -> List[Dict[Any, Any]]:
            if not request_dict:
                return []

            filter_list = []

            exlcuded_keys = [
                "page",
                "query",
                "EPIC",
                "msg",
                "advanced",
                "error",
                "success",
                "warning",
            ]

            for key, value in request_dict.items():
                if key not in exlcuded_keys:
                    filter_list.append({"key": key, "value": value})

            return filter_list

        def build_filter_query(request_dict: Dict[Any, Any], user: Users) -> List[str]:
            """Build filter query from items."""
            if not request_dict:
                return []

            filter_query = []

            if (
                not user.has_perm("Show Advanced Search")  # type: ignore[no-untyped-call]
                or "advanced" not in request_dict
                or "advanced" in request_dict
                and request_dict["advanced"] != "Y"
            ):
                # users cannot access advanced search, so add param for just visible stuff.
                filter_query.append("visible_text:(Y)")

            exlcuded_keys = [
                "page",
                "query",
                "type",
                "EPIC",
                "msg",
                "field",
                "advanced",
                "error",
                "success",
                "warning",
            ]

            for key, value in request_dict.items():
                if key not in exlcuded_keys:
                    value = " OR ".join(
                        [f"{{!tag={key}}}{key}:({v.strip()})" for v in value]
                    )
                    filter_query.append(value)

            return filter_query

        if search_string:
            hl = "*"
            hl_match = "false"

            if "field" in request_dict:
                hl = request_dict["field"][0]
                hl_match = "true"

            search_string_built = build_search_string(search_string, request_dict)
            search_filter_built = build_filter_query(request_dict, self.request.user)

            # create a solr instance, based on the search type.
            solr = pysolr.Solr(
                settings.SOLR_URL, search_handler=search_type.replace("terms", "aterms")
            )

            # pylint: disable=C0301
            results = solr.search(
                search_string_built,
                fq=search_filter_built,
                rq="{!rerank reRankQuery=$rqq reRankDocs=1000 reRankWeight=5}",
                **{"hl.fl": hl, "hl.requiredMatchField": hl_match},
                rqq='(type:collections^2.8 OR type:reports^2 OR documented:Y^0.1 OR executive_visibility:Y^0.2  OR certification:"Analytics Certified"^0.4 OR certification:"Analytics Reviewed"^0.4)',
                start=page - 1,
                rows=max_results,
            )

            # pagination
            page_count = math.ceil(results.hits / max_results)

            page_from = max(1, page - page_slide)
            page_to = min(page_count - 1, page + page_slide)

            page_from = max(1, min(page_to - 2 * page_slide, page_from))
            page_to = min(page_count, max(page_from + 2 * page_slide, page_to))

            context["pages"] = range(page_from, page_to - page_from + 1)

            context["facets"] = {}
            context["hits"] = results.hits
            context["page_index"] = page
            context["next_page"] = page + 1
            context["previous_page"] = page - 1
            context["qtime"] = results.qtime
            context["last_page"] = page_count
            context["search_string"] = search_string
            context["search_filters"] = build_filter_list(request_dict)
            context["filter_fields"] = build_filter_fields(search_type)
            context["advanced"] = (
                "Y"
                if self.request.user.has_perm("Show Advanced Search")
                and request_dict.get("advanced", "N") == "Y"
                else "N"
            )

            with contextlib.suppress(AttributeError):
                context["facets"] = copy.deepcopy(results.facets)

                facet_fields = []
                for attr, _value in clean_dict(
                    results.facets.get("facet_fields").items()
                ).items():
                    fields = results.facets.get("facet_fields").get(attr)

                    facet_order = [
                        "type",
                        "report_type_text",
                        "certification_text",
                        "visible_text",
                        "executive_visiblity_text",
                        "fragility_text",
                        "maintenance_schedule_text",
                        "estimated_run_frequency_text",
                        "organizational_value_text",
                        "epic_master_file_text",
                    ]

                    facet_fields.append(
                        {
                            "key": attr,
                            "value": [
                                {"key": field, "value": fields[(num * 2) + 1]}
                                for num, field in enumerate(fields[::2])
                            ],
                        }
                    )

                context["facets"]["facet_fields"] = sorted(
                    facet_fields,
                    key=lambda item: facet_order.index(item.get("key"))  # type: ignore[arg-type]
                    if item.get("key") in facet_order
                    else 999,
                )

            result_set = []

            for match in results.docs:
                if match["type"] == "reports":
                    result_set.append(
                        {
                            "id": match["id"],
                            "matched_field": list(
                                results.highlighting[match["id"]].keys()
                            )[0]
                            if results.highlighting[match["id"]]
                            else None,
                            "report": Reports.objects.select_related("docs")
                            .select_related("type")
                            .prefetch_related("attachments")
                            .prefetch_related("starred")
                            .prefetch_related("tags__tag")
                            .prefetch_related(
                                Prefetch("imgs", ReportImages.objects.order_by("rank"))
                            )
                            .get(pk=match["atlas_id"]),
                        }
                    )
                elif match["type"] == "terms":
                    result_set.append(
                        {
                            "id": match["id"],
                            "matched_field": list(
                                results.highlighting[match["id"]].keys()
                            )[0]
                            if results.highlighting[match["id"]]
                            else None,
                            "term": Terms.objects.prefetch_related("starred").get(
                                pk=match["atlas_id"]
                            ),
                        }
                    )
                elif match["type"] == "initiatives":
                    result_set.append(
                        {
                            "id": match["id"],
                            "matched_field": list(
                                results.highlighting[match["id"]].keys()
                            )[0]
                            if results.highlighting[match["id"]]
                            else None,
                            "initiative": Initiatives.objects.get(pk=match["atlas_id"]),
                        }
                    )
                elif match["type"] == "collections":
                    result_set.append(
                        {
                            "id": match["id"],
                            "matched_field": list(
                                results.highlighting[match["id"]].keys()
                            )[0]
                            if results.highlighting[match["id"]]
                            else None,
                            "collection": Collections.objects.get(pk=match["atlas_id"]),
                        }
                    )
                elif match["type"] == "users":
                    result_set.append(
                        {
                            "id": match["id"],
                            "matched_field": list(
                                results.highlighting[match["id"]].keys()
                            )[0]
                            if results.highlighting[match["id"]]
                            else None,
                            "user": Users.objects.get(pk=match["atlas_id"]),
                        }
                    )
                elif match["type"] == "groups":
                    result_set.append(
                        {
                            "id": match["id"],
                            "matched_field": list(
                                results.highlighting[match["id"]].keys()
                            )[0]
                            if results.highlighting[match["id"]]
                            else None,
                            "group": Groups.objects.get(pk=match["atlas_id"]),
                        }
                    )
            context["results"] = result_set
        return context


def clean_dict(my_dict: Dict[Any, Any]) -> Dict[Any, Any]:
    """Remove none values from dict."""
    return {attr: value for attr, value in my_dict if value}


def build_search_string(
    search_string: str, query: Optional[Dict[Any, Any]] = None
) -> str:
    """Escape invalid chars."""
    if query is None:
        query = {}
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
        "~",
        "*",
        "?",
        ":",
        "/",
    )

    if search_string is None:
        return "*"

    # clean search string
    for char in reserved_characters:
        search_string = search_string.replace(char, f"\\{char}")

    def special_to_lower(match: re.Match) -> str:
        return match.group(0).lower()

    search_string = re.sub(r"\b(OR|AND|NOT)\b", special_to_lower, search_string)
    # get exact matches
    exact_matches = []

    for literal in re.finditer(r"(\")(.+?)(\")", search_string):
        if "field" in query:
            field = query.get("field")
            exact_matches.append(f'{field}:"{literal.groups(2)}"')

        else:
            exact_matches.append(
                " ".join(
                    (
                        f'name:"{literal.groups(2)}"^8 OR',
                        f'description: "{literal.groups(2)}"^5 OR',
                        f'email: "{literal.groups(2)}" OR',
                        f'external_url: "{literal.groups(2)}" OR',
                        f'financial_impact: "{literal.groups(2)}" OR',
                        f'fragility_tags: "{literal.groups(2)}" OR',
                        f'group_type: "{literal.groups(2)}" OR',
                        f'linked_description: "{literal.groups(2)}" OR',
                        f'maintenance_schedule: "{literal.groups(2)}" OR',
                        f'operations_owner: "{literal.groups(2)}" OR',
                        f'organizational_value: "{literal.groups(2)}" OR',
                        f'related_collections: "{literal.groups(2)}" OR',
                        f'related_initiatives: "{literal.groups(2)}" OR',
                        f'related_reports: "{literal.groups(2)}" OR',
                        f'related_terms: "{literal.groups(2)}" OR',
                        f'report_last_updated_by: "{literal.groups(2)}" OR',
                        f'report_type: "{literal.groups(2)}" OR',
                        f'requester: "{literal.groups(2)}" OR',
                        f'source_database: "{literal.groups(2)}" OR',
                        f'strategic_importance: "{literal.groups(2)}" OR',
                        f'updated_by: "{literal.groups(2)}" OR',
                        f'user_groups: "{literal.groups(2)}" OR',
                        f'user_roles: "{literal.groups(2)}" OR',
                        f'source_database: "{literal.groups(2)}"',
                    )
                )
            )

    search_string = re.sub(r"(\".+?\")", "", search_string)

    # clean up remaining quotes
    search_string = re.sub(r"\"", '\\\\"', search_string)

    def build_exact(wild: str, exact: List[str]) -> str:
        if len(exact) == 0:
            return wild

        exact_string = " AND ".join(exact)

        if wild == "":
            return exact_string

        return f"{exact_string} AND ({wild})"

    if search_string == "":
        return build_exact("", exact_matches)

    if "field" in query:
        field = query["field"]
        return build_exact(f"{field}:({search_string})^60", exact_matches)

    return build_exact(
        f"name:({search_string})^12 OR name_split:({search_string})^6 OR description:({search_string})^5 OR description_split:({search_string})^3 OR ({search_string})",
        exact_matches,
    )

    # change search terms to fuzzy.. allow changing up to 1/2 the word
    # def build_fuzzy(sub_str):
    #     """Add fuzzy option."""
    #     if len(sub_str) > 1:
    #         fuzy_type = "~" if sub_str is None else "*~"
    #         return sub_str + fuzy_type + str(max(len(sub_str) // 3, 1))

    #     elif len(sub_str) == 1:
    #         return sub_str + "*~"

    #     return sub_str

    # search_string_fuzzy = " ".join(
    #     build_fuzzy(item) for item in search_string.split(" ")
    # )

    # return "name:({search})^6 OR name:({fuzzy})^3 OR ({search})^5 OR ({fuzzy})".format(
    #     search=search_string, fuzzy=search_string_fuzzy
    # )


@never_cache
@login_required
def user_lookup(request: HttpRequest, role: Optional[str] = None) -> JsonResponse:
    """User lookup."""
    solr = pysolr.Solr(settings.SOLR_URL, search_handler="users")

    results = solr.search(
        build_search_string(request.GET.get("s")),
        fq=(f"user_roles:{role}" if role else "*:*"),
        **{"rows": 20},
    )

    output = [
        {
            "ObjectId": item.get("atlas_id"),
            "Name": item.get("name")
            + (" (" + item["email"] + ")" if item.get("email") else ""),
        }
        for item in results
    ]
    return JsonResponse(output, safe=False)


@never_cache
@login_required
def group_lookup(request: HttpRequest, role: Optional[str] = None) -> JsonResponse:
    """User lookup."""
    solr = pysolr.Solr(settings.SOLR_URL, search_handler="groups")

    results = solr.search(
        build_search_string(request.GET.get("s")),
        fq=(f"user_roles:{role}" if role else "*:*"),
        **{"rows": 20},
    )

    output = [
        {
            "ObjectId": item.get("atlas_id"),
            "Name": item.get("name")
            + (" (" + item["email"] + ")" if item.get("email") else ""),
        }
        for item in results
    ]
    return JsonResponse(output, safe=False)


@never_cache
@login_required
def director_lookup(request: HttpRequest) -> HttpResponse:
    """Director lookup."""
    return redirect(user_lookup, role="Director")


@never_cache
@login_required
def collection_lookup(request: HttpRequest) -> JsonResponse:
    """Dropdown lookup for collections."""
    search_string = build_search_string(request.GET.get("s"))

    solr = pysolr.Solr(settings.SOLR_URL, search_handler="collections")

    results = solr.search(build_search_string(search_string), **{"rows": 20})

    output = [
        {"ObjectId": item.get("atlas_id"), "Name": item.get("name")} for item in results
    ]
    return JsonResponse(output, safe=False)


@never_cache
@login_required
def report_lookup(request: HttpRequest) -> JsonResponse:
    """Report lookup."""
    search_string = build_search_string(request.GET.get("s"))

    solr = pysolr.Solr(settings.SOLR_URL, search_handler="reports")

    results = solr.search(build_search_string(search_string), **{"rows": 20})

    output = [
        {"ObjectId": item.get("atlas_id"), "Name": item.get("name")} for item in results
    ]
    return JsonResponse(output, safe=False)


@never_cache
@login_required
def term_lookup(request: HttpRequest) -> JsonResponse:
    """Term lookup."""
    search_string = build_search_string(request.GET.get("s"))

    solr = pysolr.Solr(settings.SOLR_URL, search_handler="aterms")

    results = solr.search(build_search_string(search_string), **{"rows": 20})

    output = [
        {"ObjectId": item.get("atlas_id"), "Name": item.get("name")} for item in results
    ]
    return JsonResponse(output, safe=False)


@never_cache
@login_required
def dropdown_lookup(request: HttpRequest, lookup: str) -> JsonResponse:
    """Mini search for dropdowns."""
    solr = pysolr.Solr(settings.SOLR_LOOKUP_URL)

    lookup_values = [
        {"ObjectId": value.get("atlas_id"), "Name": value.get("item_name")}
        for value in solr.search("item_type:%s" % lookup, **{"rows": 9999})
    ]

    return JsonResponse(lookup_values, safe=False)
