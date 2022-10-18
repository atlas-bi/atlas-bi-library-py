"""Atlas user roles settings."""
# pylint: disable=C0115, W0613, C0116
from typing import Any, Dict, Tuple

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.views.generic import DeleteView, TemplateView, UpdateView
from index.models import (
    GroupRoleLinks,
    RolePermissionLinks,
    RolePermissions,
    UserRolelinks,
    UserRoles,
)

from atlas.decorators import NeverCacheMixin, PermissionsCheckMixin


class Index(NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    template_name = "settings/roles.html.dj"
    required_permissions = (
        "Manage Global Site Settings",
        "Edit Role Permissions",
    )

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        """Add context to request."""
        context = super().get_context_data(**kwargs)
        context["roles"] = UserRoles.objects.prefetch_related(
            "permission_links", "permission_links__permission"
        ).all()
        context["permissions"] = RolePermissions.objects.all()
        context["locked_roles"] = ("User", "Administrator", "Director")
        return context

    def post(
        self, request: HttpRequest, *args: Tuple[Any], **kwargs: Dict[Any, Any]
    ) -> HttpResponse:
        if not request.POST.get("name"):
            return redirect(
                reverse("settings:index") + "?error=Role name is required.#roles"
            )

        UserRoles(name=request.POST.get("name")).save()

        return redirect(
            reverse("settings:index") + "?success=Role successfully saved.#roles"
        )


class Delete(NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, DeleteView):
    required_permissions = (
        "Manage Global Site Settings",
        "Edit Role Permissions",
    )
    model = UserRoles
    template_name = "settings/roles.html.dj"

    def get_success_url(self) -> str:
        return reverse("settings:index") + "?success=Role successfully deleted.#roles"

    def get(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> HttpResponse:
        return redirect(
            resolve("settings:index")
            + "?error=You are not authorized to access that page.#roles"
        )

    def post(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> HttpResponse:
        pk = self.kwargs["pk"]
        RolePermissionLinks.objects.filter(role__role_id=pk).delete()
        GroupRoleLinks.objects.filter(role__role_id=pk).delete()
        UserRolelinks.objects.filter(role__role_id=pk).delete()
        return super().post(*args, **kwargs)


class Permission(
    NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, UpdateView
):
    required_permissions = (
        "Manage Global Site Settings",
        "Edit Role Permissions",
    )

    def post(
        self, request: HttpRequest, *args: Tuple[Any], **kwargs: Dict[Any, Any]
    ) -> HttpResponse:
        pk = self.kwargs["pk"]
        permission_pk = self.kwargs["permission_pk"]

        if RolePermissionLinks.objects.filter(
            role_id=pk, permission_id=permission_pk
        ).exists():
            RolePermissionLinks.objects.filter(
                role_id=pk, permission_id=permission_pk
            ).delete()
        else:
            RolePermissionLinks(role_id=pk, permission_id=permission_pk).save()

        return HttpResponse("updated")
