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
from index.models import (
    FinancialImpact,
    Fragility,
    FragilityTag,
    InitiativeContacts,
    MaintenanceLogStatus,
    MaintenanceSchedule,
    OrganizationalValue,
    ProjectMilestoneFrequency,
    ProjectMilestoneTemplates,
    Projects,
    RunFrequency,
    StrategicImportance,
    UserRoles,
)


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
        - adds project ads

    Still need to add facet ranges

    """
    if request.method == "GET":
        context = {
            "permissions": request.user.get_permissions(),
            "user": request.user,
            "favorites": request.user.get_favorites(),
        }

        return render(request, "search.html.dj", context)

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

    # break early if project, otherwise get project ads.
    if search_type == "projects":
        return JsonResponse(output, safe=False)

    output["projects"] = build_project_ads(results.docs)

    return JsonResponse(output, safe=False)


def clean_dict(my_dict):
    """Remove none values from dict."""
    return {attr: value for attr, value in my_dict if value}


def build_project_ads(docs):
    """Build project ad lists."""

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

    # get projects from results
    return list(
        Projects.objects.filter(
            Q(term_annotations__term__term_id__in=term_ids)
            | Q(report_annotations__report__report_id__in=report_ids)
        )
        .filter(Q(hidden__isnull=True) | Q(hidden="N"))
        .all()
        .values("project_id", "purpose", "description", "name")
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

    def build_fuzzy(sub_str):
        """Add fuzzy option."""
        if len(sub_str) > 1:
            fuzy_type = "~" if sub_str is None else "*~"
            return sub_str + fuzy_type + str(max(len(sub_str) // 3, 1))

        return sub_str

    # clean search string
    for char in reserved_characters:
        search_string = search_string.replace(char, "\\%s" % char)

    # change search terms to fuzzy.. allow changing up to 1/2 the word
    search_string_fuzzy = " ".join(
        build_fuzzy(item) for item in search_string.split(" ")
    )

    return "name:({search})^6 OR name:({search_fuzzy})^3 OR ({search})^5 OR ({search_fuzzy})".format(
        search=search_string, search_fuzzy=search_string_fuzzy
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
def user_lookup(request):
    """User lookup."""
    search_string = build_search_string(request.GET.get("s", ""), search_type="fuzzy")

    solr = pysolr.Solr(settings.SOLR_URL, search_handler="users")

    results = solr.search(build_search_string(search_string), **{"rows": 20})

    output = [
        {"ObjectId": item.get("atlas_id"), "Name": item.get("name")} for item in results
    ]
    return JsonResponse(output, safe=False)


@never_cache
@login_required
def project_lookup(request):
    """Project lookup."""
    search_string = build_search_string(request.GET.get("s", ""), search_type="fuzzy")

    solr = pysolr.Solr(settings.SOLR_URL, search_handler="projects")

    results = solr.search(build_search_string(search_string), **{"rows": 20})

    output = [
        {"ObjectId": item.get("atlas_id"), "Name": item.get("name")} for item in results
    ]
    return JsonResponse(output, safe=False)


@never_cache
@login_required
def lookup(request, lookup):
    """Mini search for dropdowns."""
    lookup_values = []
    if lookup == "org-value":
        lookup_values = [
            {"ObjectId": value.value_id, "Name": value.name}
            for value in OrganizationalValue.objects.all()
        ]

    elif lookup == "run-freq":
        lookup_values = [
            {"ObjectId": value.frequency_id, "Name": value.name}
            for value in RunFrequency.objects.all()
        ]

    elif lookup == "fragility":
        lookup_values = [
            {"ObjectId": value.fragility_id, "Name": value.name}
            for value in Fragility.objects.all()
        ]

    elif lookup == "maint-sched":
        lookup_values = [
            {"ObjectId": value.schedule_id, "Name": value.name}
            for value in MaintenanceSchedule.objects.all()
        ]

    elif lookup == "ro-fragility":
        lookup_values = [
            {"ObjectId": value.tag_id, "Name": value.name}
            for value in FragilityTag.objects.all()
        ]

    elif lookup == "maint-log-stat":
        lookup_values = [
            {"ObjectId": value.status_id, "Name": value.name}
            for value in MaintenanceLogStatus.objects.all()
        ]

    elif lookup == "ext-cont":
        lookup_values = [
            {"ObjectId": value.contact_id, "Name": value.name}
            for value in InitiativeContacts.objects.all()
        ]

    elif lookup == "mile-temp":
        lookup_values = [
            {"ObjectId": value.frequency_id, "Name": value.name}
            for value in ProjectMilestoneFrequency.objects.all()
        ]

    elif lookup == "mile-type":
        lookup_values = [
            {"ObjectId": value.template_id, "Name": value.name}
            for value in ProjectMilestoneTemplates.objects.all()
        ]

    elif lookup == "user-roles":
        lookup_values = [
            {"ObjectId": value.role_id, "Name": value.name}
            for value in UserRoles.objects.all()
        ]

    elif lookup == "financial-impact":
        lookup_values = [
            {"ObjectId": value.impact_id, "Name": value.name}
            for value in FinancialImpact.objects.all()
        ]

    elif lookup == "strategic-importance":
        lookup_values = [
            {"ObjectId": value.importance_id, "Name": value.name}
            for value in StrategicImportance.objects.all()
        ]

    return JsonResponse(lookup_values, safe=False)
