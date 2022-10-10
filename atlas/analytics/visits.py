"""Atlas analytics views."""
import json
import math
from datetime import datetime, timedelta
from statistics import mean

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, F, Max, PositiveIntegerField, Sum
from django.db.models.functions import Cast, Trunc
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from index.models import Analytics, Groups, Users

from atlas.decorators import admin_required


class Index(LoginRequiredMixin, TemplateView):
    template_name = "analytics/visits.html.dj"

    def get(self, *args, **kwargs):

        start_at = int(self.request.GET.get("start_at", -86400))
        end_at = int(self.request.GET.get("end_at", 0))
        user_id = self.request.GET.get("user_id", -1)
        group_id = self.request.GET.get("group_id", -1)

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
            subquery = subquery.filter(user__group__id=group_id)

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
                "views": sum([x["pages"] for x in access_history]),
                "visitors": sum([x["sessions"] for x in access_history]),
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


@login_required
def browsers(request):
    return HttpResponse("ok")


@login_required
def os(request):
    return HttpResponse("ok")


@login_required
def resolution(request):
    return HttpResponse("ok")


@login_required
def users(request):
    return HttpResponse("ok")


@login_required
def load_time(request):
    return HttpResponse("ok")
