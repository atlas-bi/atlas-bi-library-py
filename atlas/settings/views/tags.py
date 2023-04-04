"""Atlas settings tags views."""
# pylint: disable=C0115, W0613, C0116
from typing import Any, Dict, Tuple

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import HttpResponseRedirect, redirect
from django.urls import resolve, reverse
from django.views.generic import DeleteView, TemplateView
from index.models import (
    FinancialImpact,
    Fragility,
    FragilityTag,
    MaintenanceLogStatus,
    MaintenanceSchedule,
    OrganizationalValue,
    ReportDocs,
    RunFrequency,
    StrategicImportance,
    Tags,
    UserRolelinks,
)

from atlas.decorators import NeverCacheMixin, PermissionsCheckMixin


class Index(NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    template_name = "settings/tags.html.dj"
    required_permissions = ("Manage Global Site Settings",)

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        """Add context to request."""
        tag_type = self.kwargs["tag_type"]
        context = super().get_context_data(**kwargs)

        if tag_type == "run_frequency":
            context["placeholder"] = "centuryly"
            context["tags"] = RunFrequency.objects.all()
        elif tag_type == "tags":
            context["placeholder"] = "certified"
            context["tags"] = Tags.objects.all()
        elif tag_type == "financial_impact":
            context["placeholder"] = "massive"
            context["tags"] = FinancialImpact.objects.all()
        elif tag_type == "fragility":
            context["placeholder"] = "plate glass"
            context["tags"] = Fragility.objects.all()
        elif tag_type == "fragility_tag":
            context["placeholder"] = "gonna bust"
            context["tags"] = FragilityTag.objects.all()
        elif tag_type == "maintenance_log_status":
            context["placeholder"] = "checked out"
            context["tags"] = MaintenanceLogStatus.objects.all()
        elif tag_type == "maintenance_schedule":
            context["placeholder"] = "bi-quarterly"
            context["tags"] = MaintenanceSchedule.objects.all()
        elif tag_type == "organizational_value":
            context["placeholder"] = "invaluable"
            context["tags"] = OrganizationalValue.objects.all()
        elif tag_type == "strategic_importance":
            context["placeholder"] = "critical"
            context["tags"] = StrategicImportance.objects.all()

        return context

    def post(
        self, request: HttpRequest, *args: Tuple[Any], **kwargs: Dict[Any, Any]
    ) -> HttpResponse:
        tag_type = self.kwargs["tag_type"]

        if not request.POST.get("name"):
            return redirect(
                reverse("settings:index") + "?error=Tag name is required.#meta-fields"
            )
        if tag_type == "run_frequency":
            RunFrequency(name=request.POST.get("name")).save()
        elif tag_type == "tags":
            Tags(
                name=request.POST.get("name"),
                description=request.POST.get("description"),
                show_in_header=request.POST.get("show_in_header"),
            ).save()
        elif tag_type == "financial_impact":
            FinancialImpact(name=request.POST.get("name")).save()
        elif tag_type == "fragility":
            Fragility(name=request.POST.get("name")).save()
        elif tag_type == "fragility_tag":
            FragilityTag(name=request.POST.get("name")).save()
        elif tag_type == "maintenance_log_status":
            MaintenanceLogStatus(name=request.POST.get("name")).save()
        elif tag_type == "maintenance_schedule":
            MaintenanceSchedule(name=request.POST.get("name")).save()
        elif tag_type == "organizational_value":
            OrganizationalValue(name=request.POST.get("name")).save()
        elif tag_type == "strategic_importance":
            StrategicImportance(name=request.POST.get("name")).save()

        return redirect(
            reverse("settings:index") + "?success=Tag successfully added.#meta-fields"
        )


class Delete(NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, DeleteView):
    required_permissions = ("Manage Global Site Settings",)
    model = UserRolelinks
    template_name = "settings/user_roles.html.dj"

    def get_success_url(self) -> str:
        return (
            reverse("settings:index") + "?success=Tag successfully deleted.#meta-fields"
        )

    def get(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> HttpResponse:
        return redirect(
            resolve("settings:index")
            + "?error=You are not authorized to access that page.#meta-fields"
        )

    def post(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> HttpResponse:
        pk = self.kwargs["pk"]
        tag_type = self.kwargs["tag_type"]

        if tag_type == "run_frequency":
            ReportDocs.objects.filter(frequency_id=pk).update(frequency_id=None)
            RunFrequency.objects.filter(pk=pk).delete()
        elif tag_type == "tags":
            Tags.objects.filter(pk=pk).delete()
        elif tag_type == "financial_impact":
            FinancialImpact.objects.filter(pk=pk).delete()
        elif tag_type == "fragility":
            Fragility.objects.filter(pk=pk).delete()
        elif tag_type == "fragility_tag":
            FragilityTag.objects.filter(pk=pk).delete()
        elif tag_type == "maintenance_log_status":
            MaintenanceLogStatus.objects.filter(pk=pk).delete()
        elif tag_type == "maintenance_schedule":
            MaintenanceSchedule.objects.filter(pk=pk).delete()
        elif tag_type == "organizational_value":
            ReportDocs.objects.filter(org_value_id=pk).update(org_value_id=None)
            OrganizationalValue.objects.filter(pk=pk).delete()
        elif tag_type == "strategic_importance":
            StrategicImportance.objects.filter(pk=pk).delete()

        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)
