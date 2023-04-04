"""Atlas ETL Settings."""
# pylint: disable=C0115, W0613, C0116
from pathlib import Path
from typing import Any, Dict, Tuple

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, reverse
from django.views.generic.base import TemplateView
from index.models import GlobalSettings

from atlas.decorators import NeverCacheMixin, PermissionsCheckMixin


class Index(NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    template_name = "settings/etl.html.dj"
    required_permissions = ("Manage Global Site Settings",)

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        """Add context to request."""
        context = super().get_context_data(**kwargs)
        context["etl"] = GlobalSettings.objects.filter(name="report_tag_etl").first()

        return context

    def post(
        self, request: HttpRequest, *args: Tuple[Any], **kwargs: Dict[Any, Any]
    ) -> HttpResponse:
        setting, _ = GlobalSettings.objects.get_or_create(name="report_tag_etl")
        setting.value = request.POST.get("value", None)
        setting.save()

        return redirect(
            reverse("settings:index") + "?success=Etl successfully saved.#etl"
        )


@login_required
def default(request: HttpRequest) -> HttpResponse:
    if not request.user.has_perm("Manage Global Site Settings"):
        return HttpResponse("", content_type="text/plain")

    return HttpResponse(
        Path(settings.DEFAULT_ROOT / "report_tags_etl.sql").read_text(encoding="utf8"),
        content_type="text/plain",
    )
