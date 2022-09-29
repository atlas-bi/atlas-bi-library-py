"""Atlas settings tags views."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.views.generic import DeleteView, TemplateView
from index.models import GlobalSettings

from atlas.decorators import NeverCacheMixin, PermissionsCheckMixin


class Index(NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    template_name = "settings/site_messages.html.dj"
    required_permissions = ("Manage Global Site Settings",)

    def get_context_data(self, **kwargs):
        """Add context to request."""
        context = super().get_context_data(**kwargs)
        context["messages"] = GlobalSettings.objects.filter(name="msg").all()

        return context

    def post(self, request, *args, **kwargs):
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

    def get_success_url(self):
        return (
            reverse("settings:index")
            + "?success=Site message successfully deleted.#site-message"
        )

    def get(self, *args, **kwargs):
        return redirect(
            resolve("settings:index")
            + "?error=You are not authorized to access that page.#site-message"
        )
