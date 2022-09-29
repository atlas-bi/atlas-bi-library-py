"""Atlas group role settings."""
from django.contrib.auth.mixins import LoginRequiredMixin
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

    def get_context_data(self, **kwargs):
        """Add context to request."""
        context = super().get_context_data(**kwargs)
        context["privaledged_groups"] = (
            GroupRoleLinks.objects.prefetch_related("group", "role")
            .order_by("group__name")
            .all()
        )
        return context

    def post(self, request, *args, **kwargs):
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

    def get_success_url(self):

        return (
            reverse("settings:index")
            + "?success=Role successfully deleted.#group-roles"
        )

    def get(self, *args, **kwargs):
        return redirect(
            resolve("settings:index")
            + "?error=You are not authorized to access that page.#group-roles"
        )
