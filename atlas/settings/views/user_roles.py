"""Atlas user roles settings."""
# pylint: disable=C0115, W0613, C0116
from typing import Any, Dict, Tuple

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.views.generic import DeleteView, TemplateView
from index.models import UserRolelinks

from atlas.decorators import NeverCacheMixin, PermissionsCheckMixin


class Index(NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    template_name = "settings/user_roles.html.dj"
    required_permissions = (
        "Manage Global Site Settings",
        "Edit User Permissions",
    )

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        """Add context to request."""
        context = super().get_context_data(**kwargs)
        context["privaledged_users"] = (
            UserRolelinks.objects.prefetch_related("user", "role")
            .order_by("user__full_name")
            .all()
        )
        return context

    def post(
        self, request: HttpRequest, *args: Tuple[Any], **kwargs: Dict[Any, Any]
    ) -> HttpResponse:
        if not request.POST.get("user_id") or not request.POST.get("role_id"):
            return redirect(
                reverse("settings:index")
                + "?error=User and Role are required.#user-roles"
            )

        UserRolelinks.objects.get_or_create(
            user_id=request.POST.get("user_id"), role_id=request.POST.get("role_id")
        )

        return redirect(
            reverse("settings:index")
            + "?success=User role successfully added.#user-roles"
        )


class Delete(NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, DeleteView):
    required_permissions = (
        "Manage Global Site Settings",
        "Edit User Permissions",
    )
    model = UserRolelinks
    template_name = "settings/user_roles.html.dj"

    def get_success_url(self) -> str:
        return (
            reverse("settings:index") + "?success=Role successfully deleted.#user-roles"
        )

    def get(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> HttpResponse:
        return redirect(
            resolve("settings:index")
            + "?error=You are not authorized to access that page.#user-roles"
        )
