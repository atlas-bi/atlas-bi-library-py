"""Atlas settings tags views."""
# pylint: disable=C0115, W0613, C0116
from typing import Any, Dict, Tuple

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.views.generic import DeleteView, TemplateView
from index.models import GlobalSettings

from atlas.decorators import NeverCacheMixin, PermissionsCheckMixin


class Index(NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    template_name = "settings/site_messages.html.dj"
    required_permissions = ("Manage Global Site Settings",)

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        """Add context to request."""
        context = super().get_context_data(**kwargs)
        context["messages"] = GlobalSettings.objects.filter(name="msg").all()

        return context

    def post(
        self, request: HttpRequest, *args: Tuple[Any], **kwargs: Dict[Any, Any]
    ) -> HttpResponse:
        if not request.POST.get("value") or not request.POST.get("description"):
            return redirect(
                reverse("settings:index")
                + "?error=Id and Message are required.#site-message"
            )
        if GlobalSettings.objects.filter(
            name="msg", value=request.POST.get("value")
        ).exists():
            return redirect(
                reverse("settings:index")
                + "?error=A unique Id is required.#site-message"
            )

        GlobalSettings(
            name="msg",
            description=request.POST.get("description"),
            value=request.POST.get("value"),
        ).save()

        return redirect(
            reverse("settings:index")
            + "?success=Site message successfully added.#site-message"
        )


class Delete(NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, DeleteView):
    required_permissions = ("Manage Global Site Settings",)
    model = GlobalSettings
    template_name = "settings/user_roles.html.dj"

    def get_success_url(self) -> str:
        return (
            reverse("settings:index")
            + "?success=Site message successfully deleted.#site-message"
        )

    def get(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> HttpResponse:
        return redirect(
            resolve("settings:index")
            + "?error=You are not authorized to access that page.#site-message"
        )
