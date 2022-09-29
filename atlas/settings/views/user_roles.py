"""Atlas user roles settings."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.views.generic import DeleteView, TemplateView
from index.models import UserRolelinks

from atlas.decorators import NeverCacheMixin, PermissionsCheckMixin


class Index(NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    template_name = "settings/user_roles.html.dj"
    required_permissions = ("Manage Global Site Settings",)

    def get_context_data(self, **kwargs):
        """Add context to request."""
        context = super().get_context_data(**kwargs)
        context["privaledged_users"] = (
            UserRolelinks.objects.prefetch_related("user", "role")
            .order_by("user__full_name")
            .all()
        )
        return context

    def post(self, request, *args, **kwargs):
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
    required_permissions = ("Manage Global Site Settings",)
    model = UserRolelinks
    template_name = "settings/user_roles.html.dj"

    def get_success_url(self):

        return (
            reverse("settings:index") + "?success=Role successfully deleted.#user-roles"
        )

    def get(self, *args, **kwargs):
        return redirect(
            resolve("settings:index")
            + "?error=You are not authorized to access that page.#user-roles"
        )
