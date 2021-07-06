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
from index.models import Analytics

from atlas.decorators import admin_required


@admin_required
@login_required
def index(request):
    """Analytics homepage."""
    top_user = (
        Analytics.objects.filter(access_date__gte=(timezone.now() - timedelta(days=7)))
        .values("user___first_name")
        .annotate(
            count=Count("user"), average=Avg(Cast("load_time", PositiveIntegerField()))
        )
        .order_by("-count")
    )[:10]

    top_pages = (
        Analytics.objects.filter(access_date__gte=(timezone.now() - timedelta(days=7)))
        .values("pathname")
        .annotate(
            count=Count("user"), average=Avg(Cast("load_time", PositiveIntegerField()))
        )
        .order_by("-count")
    )[:10]

    access = (
        Analytics.objects.order_by("access_date")
        .filter(
            access_date__isnull=False,
            access_date__lte=(timezone.now().replace(day=1) - timedelta(days=1)),
        )
        .annotate(month=Trunc("access_date", "month"))
        .values("month")
        .annotate(count=Count("analytics_id"))
        .order_by("month")
    )

    search = (
        Analytics.objects.order_by("access_date")
        .filter(
            access_date__isnull=False,
            access_date__lte=timezone.now().replace(day=1) - timedelta(days=1),
            pathname="/search",
        )
        .annotate(month=Trunc("access_date", "month"))
        .values("month")
        .annotate(count=Count("analytics_id"))
        .order_by("month")
    )

    report = (
        Analytics.objects.order_by("access_date")
        .filter(
            access_date__isnull=False,
            access_date__lte=timezone.now().replace(day=1) - timedelta(days=1),
            pathname="/reports",
        )
        .annotate(month=Trunc("access_date", "month"))
        .values("month")
        .annotate(count=Count("analytics_id"))
        .order_by("month")
    )

    term = (
        Analytics.objects.order_by("access_date")
        .filter(
            access_date__isnull=False,
            access_date__lte=timezone.now().replace(day=1) - timedelta(days=1),
            pathname="/terms",
        )
        .annotate(month=Trunc("access_date", "month"))
        .values("month")
        .annotate(count=Count("analytics_id"))
        .order_by("month")
    )

    project = (
        Analytics.objects.order_by("access_date")
        .filter(
            access_date__isnull=False,
            access_date__lte=timezone.now().replace(day=1) - timedelta(days=1),
            pathname="/projects",
        )
        .annotate(month=Trunc("access_date", "month"))
        .values("month")
        .annotate(count=Count("analytics_id"))
        .order_by("month")
    )

    context = {
        "permissions": request.user.get_permissions(),
        "user": request.user,
        "top_users": top_user,
        "top_pages": top_pages,
        "access": access,
        "search": search,
        "report": report,
        "term": term,
        "project": project,
        "favorites": request.user.get_favorites(),
        "title": "Analytics",
    }

    return render(
        request,
        "analytics.html.dj",
        context,
    )


@login_required
@csrf_exempt
def log(request):
    """Create analytics log.

    1. check if session + page exists
    2. if yes > update time
    3. if no > create
    """
    log_data = json.loads(request.body.decode("utf-8"))

    log_time = timezone.now()

    analytic = (
        Analytics.objects.filter(user=request.user)
        .filter(session_id=log_data.get("sessionId"))
        .filter(page_id=log_data.get("pageId"))
    )

    if analytic.exists():
        analytic = analytic.first()
        analytic.page_time = log_data.get("pageTime")
        analytic.update_time = log_time
        analytic.save()

        return HttpResponse("ok")

    analytic = Analytics(
        username=request.user.full_name,
        app_code_name=log_data.get("appCodeName", ""),
        app_name=log_data.get("appName", ""),
        app_version=log_data.get("appVersion", ""),
        cookie_enabled=log_data.get("cookieEnabled", ""),
        language=log_data.get("language", ""),
        oscpu=log_data.get("oscpu", ""),
        platform=log_data.get("platform", ""),
        useragent=log_data.get("userAgent", ""),
        host=log_data.get("host", ""),
        hostname=log_data.get("hostname", ""),
        href=log_data.get("href", ""),
        protocol=log_data.get("protocol", ""),
        search=log_data.get("search", ""),
        pathname=log_data.get("pathname", ""),
        unique_id=log_data.get("hash", ""),
        screen_height=log_data.get("screenHeight", ""),
        screen_width=log_data.get("screenWidth", ""),
        origin=log_data.get("origin", ""),
        title=log_data.get("title", ""),
        load_time=log_data.get("loadTime", ""),
        access_date=log_time,
        referrer=log_data.get("referrer", ""),
        user=request.user,
        zoom=log_data.get("zoom", ""),
        epic=log_data.get("epic", None),
        page_id=log_data.get("pageId", ""),
        session_id=log_data.get("sessionId", ""),
        page_time=log_data.get("pageTime", ""),
        update_time=log_time,
    )

    analytic.save()

    return HttpResponse("ok")
