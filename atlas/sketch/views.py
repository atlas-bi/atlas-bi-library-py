"""Atlas Profiles."""
# pylint: disable=C0115, C0116, R0912, R0914, R0915, R0916, W0613
from datetime import datetime, timedelta
from statistics import mean
from typing import Any, Dict, Tuple

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, F, Max, Sum
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView, View
from index.models import (
    Collections,
    Groups,
    ReportRunBridge,
    Reports,
    ReportSubscriptions,
    StarredCollections,
    StarredReports,
    StarredTerms,
    Terms,
    Users,
)


class Index(LoginRequiredMixin, TemplateView):
    template_name = "sketch/index.html.dj"

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Profile"
        return context


class BaseFilter:
    request: HttpRequest = None
    kwargs: Dict[Any, Any] = {}

    def get_bridge(self) -> Tuple[ReportRunBridge, str]:
        # start and end offset from now in seconds
        start_at = int(self.request.GET.get("start_at", -31536000))  # last 12 months
        end_at = int(self.request.GET.get("end_at", 0))  # now

        # filters
        server = self.request.GET.getlist("server")
        database = self.request.GET.getlist("database")
        system_identifier = self.request.GET.getlist("system_identifier")
        visible = self.request.GET.getlist("visible")
        certification = self.request.GET.getlist("certification")
        availability = self.request.GET.getlist("availability")
        report_type = self.request.GET.getlist("report_type")
        now = timezone.now()

        start_absolute = now + timedelta(seconds=start_at)
        end_absolute = now + timedelta(seconds=end_at)

        duration = end_at - start_at

        date_format = "%-I %p"

        if duration < 172800:
            date_format = "%-I %p"
            bridges = ReportRunBridge.objects.filter(
                run__runstarttime_hour__gte=start_absolute,
                run__runstarttime_hour__lte=end_absolute,
            ).values(group_date=F("run__runstarttime_hour"))

        elif duration < 691200:
            date_format = "%a %m/%-d"
            bridges = ReportRunBridge.objects.filter(
                run__runstarttime_day__gte=start_absolute,
                run__runstarttime_day__lte=end_absolute,
            ).values(group_date=F("run__runstarttime_day"))

        elif duration < 31536000:
            date_format = "%b %d"
            bridges = ReportRunBridge.objects.filter(
                run__runstarttime_day__gte=start_absolute,
                run__runstarttime_day__lte=end_absolute,
            ).values(group_date=F("run__runstarttime_day"))

        else:
            date_format = "%b %y"
            bridges = ReportRunBridge.objects.filter(
                run__runstarttime_month__gte=start_absolute,
                run__runstarttime_month__lte=end_absolute,
            ).values(group_date=F("run__runstarttime_month"))

        # reports
        if (
            self.kwargs["type"] == "report"
            and Reports.objects.filter(report_id=self.kwargs["pk"]).exists()
        ):
            bridges = bridges.filter(report_id=self.kwargs["pk"])

        # terms
        elif (
            self.kwargs["type"] == "term"
            and Terms.objects.filter(term_id=self.kwargs["pk"]).exists()
        ):
            bridges = bridges.filter(report__docs__terms__term_id=self.kwargs["pk"])

        # collections
        elif (
            self.kwargs["type"] == "collection"
            and Collections.objects.filter(collection_id=self.kwargs["pk"]).exists()
        ):
            bridges = bridges.filter(
                report__collections__collection_id=self.kwargs["pk"]
            )

        elif (
            self.kwargs["type"] == "user"
            and Users.objects.filter(user_id=self.kwargs["pk"]).exists()
            or self.kwargs["type"] == "group"
            and Groups.objects.filter(group_id=self.kwargs["pk"]).exists()
            or self.kwargs["type"] == "report"
            and self.kwargs["pk"] == 0
        ):
            if self.kwargs["type"] == "user":
                bridges = bridges.filter(run__user_id=self.kwargs["pk"])
            elif self.kwargs["type"] == "group":
                bridges = bridges.filter(
                    run__user__group_links__group_id=self.kwargs["pk"]
                )

            if server:
                bridges = bridges.filter(report__system_server__in=server)

            if database:
                bridges = bridges.filter(report__system_db__in=database)

            if system_identifier:
                bridges = bridges.filter(
                    report__system_identifier__in=system_identifier
                )

            if visible:
                bridges = bridges.filter(report__visible__in=visible)

            if certification:
                bridges = bridges.filter(report__certification__name__in=certification)

            if availability:
                bridges = bridges.filter(report__availability__in=availability)

            if report_type:
                bridges = bridges.filter(report__type__name__in=report_type)

        return bridges, date_format


class RunList(LoginRequiredMixin, TemplateView, BaseFilter):
    template_name = "sketch/run_list.html.dj"

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        context = super().get_context_data(**kwargs)
        bridges, _ = self.get_bridge()
        bridges = (
            bridges.values(
                "report_id",
                name=F("report__name"),
                title=F("report__title"),
                type=F("report__type__name"),
                type_short=F("report__type__short_name"),
            )
            .annotate(run_sum=Sum("runs"), last_run=Max("run__runstarttime"))
            .order_by("-last_run")
        )

        context["run_list"] = bridges
        return context


class Chart(LoginRequiredMixin, View, BaseFilter):
    def get(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> HttpResponse:
        bridges, date_format = self.get_bridge()

        bridges = bridges.annotate(
            runs=Sum("runs"),
            user_count=Count("run__user"),
            run_time=Avg("run__rundurationseconds"),
        )

        return JsonResponse(
            {
                "runs": sum(x["runs"] for x in bridges),
                "users": sum(x["user_count"] for x in bridges),
                "run_time": round(mean([x["run_time"] for x in bridges] or [0]), 2),
                "data": {
                    "labels": [
                        datetime.strftime(x["group_date"], date_format) for x in bridges
                    ],
                    "datasets": [
                        {
                            "label": "Run Time",
                            "borderColor": "rgba(38,128,235,0.2)",
                            "backgroundColor": "transparent",
                            "type": "line",
                            "yAxisID": "2",
                            "data": [round(x["run_time"], 2) for x in bridges],
                        },
                        {
                            "label": "Runs",
                            "backgroundColor": "rgba(38,128,235,0.3)",
                            "borderColor": "rgba(38,128,235,0.4)",
                            "borderWidth": 1,
                            "stack": "bar",
                            "yAxisID": "1",
                            "data": [x["runs"] for x in bridges],
                        },
                        {
                            "label": "Users",
                            "backgroundColor": "rgba(38,128,235,0.5)",
                            "borderColor": "rgba(38,128,235,0.6)",
                            "borderWidth": 1,
                            "stack": "bar",
                            "yAxisID": "1",
                            "data": [x["user_count"] for x in bridges],
                        },
                    ],
                },
            }
        )


class UserList(LoginRequiredMixin, View, BaseFilter):
    def get(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> HttpResponse:
        bridges, _ = self.get_bridge()
        bridges = (
            bridges.values("run__user__full_name", "run__user_id")
            .annotate(run_sum=Count("runs"), rundate=Max("run__runstarttime"))
            .order_by("-run_sum")
            .all()[:10]
        )

        return JsonResponse(
            {
                "context": [
                    {
                        "key": x["run__user__full_name"],
                        "count": x["run_sum"],
                        "percent": x["run_sum"] / sum(x["run_sum"] for x in bridges),
                        "href": reverse(
                            "user:profile", kwargs={"pk": x["run__user_id"]}
                        )
                        if x["run__user_id"]
                        else "",
                        "title_one": "Top Users",
                        "date": datetime.strftime(x["rundate"], "%m/%d/%y"),
                        "title_two": "Runs",
                        "date_title": "Last Run",
                    }
                    for x in bridges
                ]
            }
        )


class Fails(LoginRequiredMixin, View, BaseFilter):
    def get(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> HttpResponse:
        bridges, _ = self.get_bridge()
        bridges = (
            bridges.values(
                "run__status",
            )
            .annotate(
                run_sum=Sum("runs"),
            )
            .order_by("-run_sum")
            .all()[:10]
        )

        return JsonResponse(
            {
                "context": [
                    {
                        "key": x["run__status"],
                        "count": x["run_sum"],
                        "percent": x["run_sum"] / sum(x["run_sum"] for x in bridges),
                        "title_one": "Failed Runs",
                        "title_two": "Fails",
                    }
                    for x in bridges
                ]
            }
        )


class ReportList(LoginRequiredMixin, View, BaseFilter):
    def get(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> HttpResponse:
        bridges, _ = self.get_bridge()
        bridges = (
            bridges.values(
                "report_id",
                name=F("report__name"),
                title=F("report__title"),
            )
            .annotate(run_sum=Count("runs"), rundate=Max("run__runstarttime"))
            .order_by("-run_sum")
            .all()[:10]
        )

        return JsonResponse(
            {
                "context": [
                    {
                        "key": x["title"] or x["name"],
                        "count": x["run_sum"],
                        "percent": x["run_sum"] / sum(x["run_sum"] for x in bridges),
                        "href": reverse("report:item", kwargs={"pk": x["report_id"]}),
                        "title_one": "Top Reports",
                        "date": datetime.strftime(x["rundate"], "%m/%d/%y"),
                        "title_two": "Runs",
                        "date_title": "Last Run",
                    }
                    for x in bridges
                ]
            }
        )


class Subscriptions(LoginRequiredMixin, TemplateView):
    template_name = "sketch/subscriptions.html.dj"

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        """Add context to request."""
        context = super().get_context_data(**kwargs)
        if (
            self.kwargs["type"] == "report"
            and Reports.objects.filter(report_id=self.kwargs["pk"]).exists()
        ):
            context["subscriptions"] = (
                ReportSubscriptions.objects.filter(report_id=self.kwargs["pk"])
                .select_related("user")
                .all()
            )
        return context


class Stars(LoginRequiredMixin, TemplateView):
    template_name = "sketch/stars.html.dj"

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        """Add context to request."""
        context = super().get_context_data(**kwargs)
        if (
            self.kwargs["type"] == "report"
            and Reports.objects.filter(report_id=self.kwargs["pk"]).exists()
        ):
            context["stars"] = (
                StarredReports.objects.filter(report_id=self.kwargs["pk"])
                .select_related("owner")
                .order_by("owner__full_name")
                .all()
            )

        elif (
            self.kwargs["type"] == "term"
            and Terms.objects.filter(term_id=self.kwargs["pk"]).exists()
        ):
            context["stars"] = (
                StarredTerms.objects.filter(term_id=self.kwargs["pk"])
                .select_related("owner")
                .order_by("owner__full_name")
                .all()
            )
        elif (
            self.kwargs["type"] == "collection"
            and Collections.objects.filter(collection_id=self.kwargs["pk"]).exists()
        ):
            context["stars"] = (
                StarredCollections.objects.filter(collection_id=self.kwargs["pk"])
                .select_related("owner")
                .order_by("owner__full_name")
                .all()
            )

        return context
