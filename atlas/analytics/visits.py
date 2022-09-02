"""Atlas analytics views."""

import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, PositiveIntegerField
from django.db.models.functions import Cast, Trunc
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from index.models import Analytics, Groups, Users

from atlas.decorators import admin_required


@login_required
def index(request):

    start_at = request.GET.get("start_at", -86400)
    end_at = request.GET.get("end_at", 0)
    user_id = request.GET.get("user_id", -1)
    group_id = request.GET.get("group_id", -1)

    """
    when start - end < 2days, use 1 AM, 2 AM...
    when start - end < 8 days use  Sun 3/20, Mon 3/21...
    when start - end < 365 days use Mar 1, Mar 2 ...
    when start - end > 365 days use Jan, Feb ...

    when using all time, get first day and last day and use the above rules
    """

    # DateTime MinDate = new DateTime(1900, 01, 01, 00, 00, 00);

    subquery = Analytics.objects.filter(
        access_date__gte=timezone.now() + timedelta(seconds=start_at)
    ).filter(access_date__lte=timezone.now() + timedelta(seconds=end_at))

    if user_id > 0 and Users.objects.filter(user_id=user_id).exists():
        subquery = subquery.filter(user_id=user_id)

    if group_id > 0 and Groups.objects.filter(group_id=group_id).exists():
        subquery = subquery.filter(user__group__id=group_id)

    dif = end_at - start_at

    # if dif < 172800:
    #     # for < 2 days
    #     # 1 AM, 2 AM etc..
    #     AccessHistory = await (
    #         from a in subquery
    #         # in linqpad, use SqlMethods.DateDiffHour instead of EF.Functions.DateDiffHour
    #         group a by MinDate.AddHours(
    #             EF.Functions.DateDiffHour(MinDate, (a.AccessDateTime ?? DateTime.Now))
    #         ) into grp
    #         orderby grp.Key
    #         select new AccessHistoryData
    #         {
    #             Date = grp.Key.ToString("h tt"),
    #             Sessions = grp.Select(x => x.SessionId).Distinct().Count(),
    #             Pages = grp.Select(x => x.PageId).Distinct().Count(),
    #             LoadTime = Math.Round(
    #                 (grp.Average(x => (long)Convert.ToDouble(x.LoadTime)) / 1000),
    #                 1
    #             )
    #         }
    #     ).ToListAsync();

    # elif dif < 691200:
    #     # for < 8 days
    #     #  Sun 3/20, Mon 3/21...
    #     AccessHistory = await (
    #         from a in subquery
    #         group a by MinDate.AddDays(
    #             EF.Functions.DateDiffDay(MinDate, (a.AccessDateTime ?? DateTime.Now))
    #         ) into grp
    #         orderby grp.Key
    #         select new AccessHistoryData
    #         {
    #             Date = grp.Key.ToString("ddd M/d"),
    #             Sessions = grp.Select(x => x.SessionId).Distinct().Count(),
    #             Pages = grp.Select(x => x.PageId).Distinct().Count(),
    #             LoadTime = Math.Round(
    #                 (grp.Average(x => (long)Convert.ToDouble(x.LoadTime)) / 1000),
    #                 1
    #             )
    #         }
    #     ).ToListAsync();

    # elif dif < 31536000:
    #     # for < 365 days
    #     # Mar 1, Mar 2
    #     AccessHistory = await (
    #         from a in subquery
    #         group a by MinDate.AddDays(
    #             EF.Functions.DateDiffDay(MinDate, (a.AccessDateTime ?? DateTime.Now))
    #         ) into grp
    #         orderby grp.Key
    #         select new AccessHistoryData
    #         {
    #             Date = grp.Key.ToString("MMM d"),
    #             Sessions = grp.Select(x => x.SessionId).Distinct().Count(),
    #             Pages = grp.Select(x => x.PageId).Distinct().Count(),
    #             LoadTime = Math.Round(
    #                 (grp.Average(x => (long)Convert.ToDouble(x.LoadTime)) / 1000),
    #                 1
    #             )
    #         }
    #     ).ToListAsync();

    # elif dif >= 31536000:
    #     AccessHistory = await (
    #         from a in subquery
    #         group a by MinDate.AddMonths(
    #             EF.Functions.DateDiffMonth(MinDate, (a.AccessDateTime ?? DateTime.Now))
    #         ) into grp
    #         orderby grp.Key
    #         select new AccessHistoryData
    #         {
    #             Date = grp.Key.ToString("MMM yy"),
    #             Sessions = grp.Select(x => x.SessionId).Distinct().Count(),
    #             Pages = grp.Select(x => x.PageId).Distinct().Count(),
    #             LoadTime = Math.Round(
    #                 (grp.Average(x => (long)Convert.ToDouble(x.LoadTime)) / 1000),
    #                 1
    #             )
    #         }
    #     ).ToListAsync();

    # Views = await subquery.CountAsync();

    # Visitors = await subquery.Select(x => x.SessionId).Distinct().CountAsync();

    # if (Views > 0)
    # {
    #     LoadTime = Math.Round(
    #         (await subquery.AverageAsync(x => (long)Convert.ToDouble(x.LoadTime)) / 1000),
    #         1
    #     );
    # }
    # else
    # {
    #     LoadTime = 0;
    # }

    return render(
        request,
        "analytics/visits.html.dj",
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
