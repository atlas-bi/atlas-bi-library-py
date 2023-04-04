"""Atlas analytics views."""
# pylint: disable=W0613,C0115,C0116
import json
from typing import Any, Dict

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from index.models import Analytics

from atlas.decorators import PermissionsCheckMixin


class Index(LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    template_name = "analytics/index.html.dj"
    required_permissions = ("View Site Analytics",)

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Analytics"
        return context


@login_required
@csrf_exempt
def log(request: HttpRequest) -> HttpResponse:
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
        language=log_data.get("language", ""),
        useragent=log_data.get("userAgent", ""),
        hostname=log_data.get("hostname", ""),
        href=log_data.get("href", ""),
        protocol=log_data.get("protocol", ""),
        search=log_data.get("search", ""),
        pathname=log_data.get("pathname", ""),
        unique_id=log_data.get("hash", ""),
        screen_height=log_data.get("screenHeight", ""),
        screen_width=log_data.get("screenWidth", ""),
        origin=log_data.get("origin", ""),
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
