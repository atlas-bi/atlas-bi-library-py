"""User settings views."""
# pylint: disable=C0115, C0116
from typing import Any, Dict, Tuple

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView, View
from index.models import UserSettings

from atlas.decorators import NeverCacheMixin


class Index(LoginRequiredMixin, NeverCacheMixin, TemplateView):
    template_name = "user/settings.html.dj"

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "User Settings"
        context["share_notification"] = UserSettings.objects.filter(
            name="share_notification", user_id=self.request.user.user_id
        ).first()
        return context


class Toggle(LoginRequiredMixin, NeverCacheMixin, View):
    def get(
        self, request: HttpRequest, *args: Tuple[Any, ...], **kwargs: Dict[Any, Any]
    ) -> HttpResponse:
        setting_name = request.GET.get("setting", None)

        setting, _ = UserSettings.objects.get_or_create(
            name=setting_name, user_id=request.user.user_id
        )
        if setting.value == "Y":
            setting.value = "N"
        else:
            setting.value = "Y"

        setting.save()

        return HttpResponse("Settings saved.")
