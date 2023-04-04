"""Atlas analytics views."""
# pylint: disable=W0613,C0115,C0116, W0105
from collections import Counter  # type: ignore
from datetime import datetime, timedelta
from statistics import mean
from typing import Any, Dict, Tuple

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import Avg, Count, F
from django.db.models.functions import Trunc
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone
from django.views.generic import View
from index.models import Analytics, Groups, Users
from ua_parser import user_agent_parser

from atlas.decorators import PermissionsCheckMixin


class AnalyticsFiltered:
    request: HttpRequest = None

    def filtered(self) -> Tuple[models.Model, int, int]:
        start_at = int(self.request.GET.get("start_at", -86400))
        end_at = int(self.request.GET.get("end_at", 0))
        user_id = int(self.request.GET.get("user_id", 0))
        group_id = int(self.request.GET.get("group_id", 0))
        """
        when start - end < 2days, use 1 AM, 2 AM...
        when start - end < 8 days use  Sun 3/20, Mon 3/21...
        when start - end < 365 days use Mar 1, Mar 2 ...
        when start - end > 365 days use Jan, Feb ...

        when using all time, get first day and last day and use the above rules
        """
        now = timezone.now()
        start_absolute = now + timedelta(seconds=start_at)
        end_absolute = now + timedelta(seconds=end_at)

        subquery = Analytics.objects.filter(
            access_date__gte=start_absolute, access_date__lte=end_absolute
        )

        if user_id > 0 and Users.objects.filter(user_id=user_id).exists():
            subquery = subquery.filter(user_id=user_id)

        if group_id > 0 and Groups.objects.filter(group_id=group_id).exists():
            subquery = subquery.filter(user__group_links__group_id=group_id)

        return subquery, start_at, end_at


class Index(LoginRequiredMixin, View, AnalyticsFiltered, PermissionsCheckMixin):
    required_permissions = ("View Site Analytics",)

    def get(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> HttpResponse:
        subquery, start_at, end_at = self.filtered()

        dif = end_at - start_at
        date_format = "%-I %p"
        if dif < 172800:
            date_format = "%-I %p"
            # for < 2 days
            # 1 AM, 2 AM etc..
            access_history = subquery.values(
                group_date=Trunc("access_date", "hour")
            ).annotate(
                load_time=Avg("load_time"),
                sessions=Count("session_id", distinct=True),
                pages=Count("page_id", distinct=True),
            )

        elif dif < 691200:
            # for < 8 days
            #  Sun 3/20, Mon 3/21...
            date_format = "%a %m/%-d"
            access_history = subquery.values(
                group_date=Trunc("access_date", "day")
            ).annotate(
                load_time=Avg("load_time"),
                sessions=Count("session_id", distinct=True),
                pages=Count("page_id", distinct=True),
            )

        elif dif < 31536000:
            # for < 365 days
            # Mar 1, Mar 2
            date_format = "%b %d"
            access_history = subquery.values(
                group_date=Trunc("access_date", "day")
            ).annotate(
                load_time=Avg("load_time"),
                sessions=Count("session_id", distinct=True),
                pages=Count("page_id", distinct=True),
            )

        else:
            date_format = "%b %y"
            access_history = subquery.values(
                group_date=Trunc("access_date", "month")
            ).annotate(
                load_time=Avg("load_time"),
                sessions=Count("session_id", distinct=True),
                pages=Count("page_id", distinct=True),
            )

        return JsonResponse(
            {
                "views": sum(x["pages"] for x in access_history),
                "visitors": sum(x["sessions"] for x in access_history),
                "load_time": round(
                    mean([x["load_time"] / 1000 for x in access_history] or [0]), 2
                ),
                "data": {
                    "labels": [
                        datetime.strftime(x["group_date"], date_format)
                        for x in access_history
                    ],
                    "datasets": [
                        {
                            "label": "Load Time",
                            "borderColor": "rgba(38,128,235,0.2)",
                            "backgroundColor": "transparent",
                            "type": "line",
                            "yAxisID": "2",
                            "data": [
                                round(x["load_time"] / 1000, 2) for x in access_history
                            ],
                        },
                        {
                            "label": "Views",
                            "backgroundColor": "rgba(38,128,235,0.3)",
                            "borderColor": "rgba(38,128,235,0.4)",
                            "borderWidth": 1,
                            "stack": "bar",
                            "yAxisID": "1",
                            "data": [x["pages"] for x in access_history],
                        },
                        {
                            "label": "Visitors",
                            "backgroundColor": "rgba(38,128,235,0.5)",
                            "borderColor": "rgba(38,128,235,0.6)",
                            "borderWidth": 1,
                            "stack": "bar",
                            "yAxisID": "1",
                            "data": [x["sessions"] for x in access_history],
                        },
                    ],
                },
            }
        )


class Browsers(LoginRequiredMixin, View, AnalyticsFiltered, PermissionsCheckMixin):
    required_permissions = ("View Site Analytics",)

    def get(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> HttpResponse:
        subquery, _, _ = self.filtered()

        total = subquery.count()

        browsers = subquery.values("useragent").annotate(count=Count("useragent"))

        def get_browser(agent: str) -> str:
            parsed = user_agent_parser.ParseUserAgent(agent)
            return (parsed["family"] or "other") + " " + (parsed["major"] or "")

        counter: Counter = Counter()
        for this_browser in browsers:
            parsed_browser = {
                get_browser(this_browser["useragent"]): this_browser["count"]
            }
            counter.update(parsed_browser)

        browsers = counter.most_common()

        data = []
        for browser in browsers[:10]:
            data.append(
                {
                    "key": browser[0],
                    "count": browser[1],
                    "percent": browser[1] / total,
                    "title_one": "Browser",
                    "title_two": "Views",
                }
            )

        return JsonResponse({"context": data})


class Os(LoginRequiredMixin, View, AnalyticsFiltered, PermissionsCheckMixin):
    required_permissions = ("View Site Analytics",)

    def get(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> HttpResponse:
        subquery, _, _ = self.filtered()

        total = subquery.count()

        oss = subquery.values("useragent").annotate(count=Count("useragent"))

        def get_os(agent: str) -> str:
            parsed = user_agent_parser.ParseOS(agent)
            return (
                (parsed["family"] or "other")
                + " "
                + (parsed["major"] or "0")
                + "."
                + (parsed["minor"] or "0")
            )

        counter: Counter = Counter()
        for this_os in oss:
            parsed_os = {get_os(this_os["useragent"]): this_os["count"]}
            counter.update(parsed_os)

        oss = counter.most_common()

        data = []
        for operating_system in oss[:10]:
            data.append(
                {
                    "key": operating_system[0],
                    "count": operating_system[1],
                    "percent": operating_system[1] / total,
                    "title_one": "Operating System",
                    "title_two": "Views",
                }
            )

        return JsonResponse({"context": data})


class Resolution(LoginRequiredMixin, View, AnalyticsFiltered, PermissionsCheckMixin):
    required_permissions = ("View Site Analytics",)

    def get(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> HttpResponse:
        subquery, _, _ = self.filtered()

        total = subquery.count()

        resolutions = (
            subquery.values("screen_height", "screen_width")
            .annotate(count=Count("pk"))
            .order_by("-count")
        )

        data = []
        for resolution in resolutions[:10]:
            data.append(
                {
                    "key": resolution["screen_width"]
                    + "x"
                    + resolution["screen_height"],
                    "count": resolution["count"],
                    "percent": resolution["count"] / total,
                    "title_one": "Window Resolution",
                    "title_two": "Views",
                }
            )

        return JsonResponse({"context": data})


class UserAnalytics(LoginRequiredMixin, View, AnalyticsFiltered, PermissionsCheckMixin):
    required_permissions = ("View Site Analytics",)

    def get(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> HttpResponse:
        subquery, _, _ = self.filtered()

        total = subquery.count()

        users = (
            subquery.values(full_name=F("user__full_name"))
            .annotate(count=Count("user__full_name"))
            .order_by("-count")
        )

        data = []
        for user in users[:10]:
            data.append(
                {
                    "key": user["full_name"],
                    "count": user["count"],
                    "percent": user["count"] / total,
                    "title_one": "Top User",
                    "title_two": "Views",
                }
            )

        return JsonResponse({"context": data})


class LoadTime(LoginRequiredMixin, View, AnalyticsFiltered, PermissionsCheckMixin):
    required_permissions = ("View Site Analytics",)

    def get(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> HttpResponse:
        subquery, _, _ = self.filtered()

        load_times = (
            subquery.values("pathname")
            .annotate(average=Avg("load_time"))
            .order_by("-average")
        )

        data = []
        for load_time in load_times[:10]:
            data.append(
                {
                    "key": load_time["pathname"],
                    "count": round(load_time["average"] / 1000, 2),
                    "title_one": "Load Times",
                    "title_two": "Seconds",
                }
            )

        return JsonResponse({"context": data})
