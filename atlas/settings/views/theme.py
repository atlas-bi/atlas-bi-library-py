from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, reverse
from django.views.generic.base import TemplateView
from index.models import GlobalSettings

from atlas.decorators import NeverCacheMixin, PermissionsCheckMixin


class Index(NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    template_name = "settings/theme.html.dj"
    required_permissions = ("Manage Global Site Settings",)

    def get_context_data(self, **kwargs):
        """Add context to request."""
        context = super().get_context_data(**kwargs)
        context["global_css"] = GlobalSettings.objects.filter(name="global_css").first()

        return context

    def post(self, request, *args, **kwargs):
        global_css = request.POST.get("global_css", None)

        setting, _ = GlobalSettings.objects.get_or_create(name="global_css")
        setting.value = global_css
        setting.save()

        return redirect(reverse("settings:index") + "#theme")
