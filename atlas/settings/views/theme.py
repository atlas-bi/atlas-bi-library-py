"""Atlas theme settings."""
# pylint: disable=C0115, W0613, C0116
from typing import Any, Dict, Tuple

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, reverse
from django.views.generic.base import TemplateView
from index.models import GlobalSettings

from atlas.decorators import NeverCacheMixin, PermissionsCheckMixin


class Index(NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    template_name = "settings/theme.html.dj"
    required_permissions = ("Manage Global Site Settings",)

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        """Add context to request."""
        context = super().get_context_data(**kwargs)
        context["global_css"] = GlobalSettings.objects.filter(name="global_css").first()

        return context

    def post(
        self, request: HttpRequest, *args: Tuple[Any], **kwargs: Dict[Any, Any]
    ) -> HttpResponse:
        global_css = request.POST.get("global_css", None)

        setting, _ = GlobalSettings.objects.get_or_create(name="global_css")
        setting.value = global_css
        setting.save()

        return redirect(reverse("settings:index") + "?success=Theme saved.#theme")
