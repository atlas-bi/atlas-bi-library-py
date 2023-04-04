"""Atlas search settings."""
# pylint: disable=C0115, W0613, C0116
from typing import Any, Dict, Tuple

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.views import View
from django.views.generic.base import TemplateView
from index.models import GlobalSettings, ReportTypes

from atlas.decorators import NeverCacheMixin, PermissionsCheckMixin


class Index(NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    template_name = "settings/search.html.dj"
    required_permissions = ("Manage Global Site Settings",)

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        """Add context to request."""
        context = super().get_context_data(**kwargs)
        context["report_types"] = ReportTypes.objects.all()
        context["group_visiblity"], _ = GlobalSettings.objects.get_or_create(
            name="groups_search_visibility"
        )
        context["user_visiblity"], _ = GlobalSettings.objects.get_or_create(
            name="users_search_visibility"
        )
        context["term_visiblity"], _ = GlobalSettings.objects.get_or_create(
            name="terms_search_visibility"
        )
        context["initiative_visiblity"], _ = GlobalSettings.objects.get_or_create(
            name="initiatives_search_visibility"
        )
        context["collection_visiblity"], _ = GlobalSettings.objects.get_or_create(
            name="collections_search_visibility"
        )

        return context

    def post(
        self, request: HttpRequest, *args: Tuple[Any], **kwargs: Dict[Any, Any]
    ) -> HttpResponse:
        search_type = self.kwargs["type"]
        report_type_id = self.kwargs["id"]

        if search_type == "reports":
            report_type = ReportTypes.objects.filter(type_id=report_type_id).first()

            if report_type.visible == "Y":
                report_type.visible = None
            else:
                report_type.visible = "Y"

            report_type.save()

        else:
            fields = {
                "users": "users_search_visibility",
                "groups": "groups_search_visibility",
                "terms": "terms_search_visibility",
                "initiatives": "initiatives_search_visibility",
                "collections": "collections_search_visibility",
            }

            setting, _ = GlobalSettings.objects.get_or_create(name=fields[search_type])
            if setting.value == "Y":
                setting.value = None
            else:
                setting.value = "Y"

            setting.save()

        return HttpResponse("Changes saved.", content_type="text/plain")


class ReportTypeName(NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, View):
    required_permissions = ("Manage Global Site Settings",)

    def get(
        self, request: HttpRequest, *args: Tuple[Any], **kwargs: Dict[Any, Any]
    ) -> HttpResponse:
        report_type_id = self.kwargs["id"]

        report_type = ReportTypes.objects.filter(type_id=report_type_id).first()
        report_type.short_name = request.GET.get("name")
        report_type.save()

        return HttpResponse("Changes saved.", content_type="text/plain")
