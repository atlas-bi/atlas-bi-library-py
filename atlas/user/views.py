"""Atlas User views."""

from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import TemplateView
from index.models import (
    Analytics,
    Collections,
    Groups,
    Initiatives,
    Reports,
    ReportSubscriptions,
    Terms,
    UserPreferences,
    UserRoles,
    Users,
)

from atlas.decorators import PermissionsCheckMixin, admin_required


class Index(LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    template_name = "user/index.html.dj"

    def get_permission_names(self):
        pk = self.kwargs["pk"]
        if pk != self.request.user.user_id:
            self.required_permissions = ("View Other User",)
        else:
            self.required_permissions = ()

        return super().get_permission_names()

    def get_context_data(self, **kwargs):
        pk = self.kwargs["pk"]
        context = super().get_context_data(**kwargs)
        context["user"] = get_object_or_404(Users, pk=pk) if pk else self.request.user
        context["is_me"] = pk is None or pk == self.request.user.user_id

        return context


@admin_required
@login_required
def roles(request):
    """Get list of user roles."""
    return JsonResponse(list(UserRoles.objects.all().values()), safe=False)


@admin_required
@login_required
def disable_admin(request):
    """Change user role."""
    next_url = request.GET.get("url", "/")

    if not url_has_allowed_host_and_scheme(next_url, request.get_host()):
        next_url = "/"

    if UserPreferences.objects.filter(key="AdminDisabled", user=request.user).exists():
        UserPreferences.objects.filter(key="AdminDisabled", user=request.user).delete()
    else:
        pref = UserPreferences(key="AdminDisabled", user=request.user)
        pref.save()

    return redirect(next_url)


class Subscriptions(LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    template_name = "user/subscriptions.html.dj"

    def get_permission_names(self):
        pk = self.kwargs["pk"]
        if pk != self.request.user.user_id:
            self.required_permissions = ("View Other User",)
        else:
            self.required_permissions = ()

        return super().get_permission_names()

    def get_context_data(self, **kwargs):
        pk = self.kwargs["pk"] or self.request.user.user_id
        context = super().get_context_data(**kwargs)
        context["subscriptions"] = ReportSubscriptions.objects.filter(
            Q(user_id=pk)
            | Q(
                email__in=Users.objects.filter(user_id=pk).values_list(
                    "group_links__group__email", flat=True
                )
            )
        ).select_related("report")

        return context


class UserGroups(LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    template_name = "user/groups.html.dj"

    def get_permission_names(self):
        pk = self.kwargs["pk"]
        if pk != self.request.user.user_id:
            self.required_permissions = ("View Other User",)
        else:
            self.required_permissions = ()

        return super().get_permission_names()

    def get_context_data(self, **kwargs):
        pk = self.kwargs["pk"] or self.request.user.user_id
        context = super().get_context_data(**kwargs)
        context["groups"] = Groups.objects.filter(user_memberships__user_id=pk)

        return context


class History(LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    template_name = "user/history.html.dj"

    def get_permission_names(self):
        pk = self.kwargs["pk"]
        if pk != self.request.user.user_id:
            self.required_permissions = ("View Other User",)
        else:
            self.required_permissions = ()

        return super().get_permission_names()

    def get_context_data(self, **kwargs):
        pk = self.kwargs["pk"] or self.request.user.user_id
        context = super().get_context_data(**kwargs)

        seven_days_ago = timezone.now() + timedelta(days=-7)
        thirty_days_ago = timezone.now() + timedelta(days=-30)
        context["history"] = Analytics.objects.filter(
            user_id=pk, access_date__gte=seven_days_ago
        ).order_by("-access_date")
        context["report_edits"] = Reports.objects.filter(
            modified_by_id=pk, modified_at__gte=thirty_days_ago
        ).order_by("-modified_at")
        context["initiative_edits"] = Initiatives.objects.filter(
            modified_by_id=pk, modified_at__gte=thirty_days_ago
        ).order_by("-modified_at")
        context["collection_edits"] = Collections.objects.filter(
            modified_by_id=pk, modified_at__gte=thirty_days_ago
        ).order_by("-modified_at")
        context["term_edits"] = Terms.objects.filter(
            modified_by_id=pk, modified_at__gte=thirty_days_ago
        ).order_by("-modified_at")

        return context
