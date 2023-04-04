"""Atlas group role settings."""
# pylint: disable=C0115, W0613, C0116
from typing import Any, Dict, Tuple

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.views.generic import DeleteView, TemplateView
from index.models import GroupRoleLinks

from atlas.decorators import NeverCacheMixin, PermissionsCheckMixin


class Index(NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    template_name = "settings/group_roles.html.dj"
    required_permissions = (
        "Manage Global Site Settings",
        "Edit Group Permissions",
    )

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        """Add context to request."""
        context = super().get_context_data(**kwargs)
        context["privaledged_groups"] = (
            GroupRoleLinks.objects.prefetch_related("group", "role")
            .order_by("group__name")
            .all()
        )
        return context

    def post(
        self, request: HttpRequest, *args: Tuple[Any], **kwargs: Dict[Any, Any]
    ) -> HttpResponse:
        if not request.POST.get("group_id") or not request.POST.get("role_id"):
            return redirect(
                reverse("settings:index")
                + "?error=Group and Role are required.#group-roles"
            )

        GroupRoleLinks.objects.get_or_create(
            group_id=request.POST.get("group_id"), role_id=request.POST.get("role_id")
        )

        return redirect(
            reverse("settings:index")
            + "?success=Group role successfully added.#group-roles"
        )


class Delete(NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, DeleteView):
    required_permissions = (
        "Manage Global Site Settings",
        "Edit Group Permissions",
    )
    model = GroupRoleLinks
    template_name = "settings/group_roles.html.dj"

    def get_success_url(self) -> str:
        return (
            reverse("settings:index")
            + "?success=Role successfully deleted.#group-roles"
        )

    def get(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> HttpResponse:
        return redirect(
            resolve("settings:index")
            + "?error=You are not authorized to access that page.#group-roles"
        )
