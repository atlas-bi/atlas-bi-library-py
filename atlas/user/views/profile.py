"""Atlas User views."""
# pylint: disable=C0115, C0116
from datetime import timedelta
from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import TemplateView
from index.models import (
    Analytics,
    Collections,
    Groups,
    Initiatives,
    Reports,
    ReportSubscriptions,
    SharedItems,
    Terms,
    Users,
)

from atlas.decorators import PermissionsCheckMixin


class Shares(LoginRequiredMixin, TemplateView):
    template_name = "user/shares.html.dj"

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        context = super().get_context_data(**kwargs)
        context["shares"] = SharedItems.objects.filter(
            recipient_id=self.request.user.user_id
        ).order_by("-share_date")
        return context


class Index(LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    template_name = "user/index.html.dj"

    def get_permission_names(self) -> Any:
        pk = self.kwargs.get("pk")
        if pk != self.request.user.user_id:
            self.required_permissions = ("View Other User",)
        else:
            self.required_permissions = ()

        return super().get_permission_names()

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        pk = self.kwargs.get("pk")
        context = super().get_context_data(**kwargs)
        context["user"] = get_object_or_404(Users, pk=pk) if pk else self.request.user
        context["is_me"] = pk is None or pk == self.request.user.user_id
        context["title"] = str(
            get_object_or_404(Users, pk=pk) if pk else self.request.user
        )

        return context


class Subscriptions(LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    template_name = "user/subscriptions.html.dj"

    def get_permission_names(self) -> Any:
        pk = self.kwargs.get("pk")
        if pk != self.request.user.user_id:
            self.required_permissions = ("View Other User",)
        else:
            self.required_permissions = ()

        return super().get_permission_names()

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        pk = self.kwargs.get("pk") or self.request.user.user_id
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

    def get_permission_names(self) -> Any:
        pk = self.kwargs.get("pk")
        if pk != self.request.user.user_id:
            self.required_permissions = ("View Other User",)
        else:
            self.required_permissions = ()

        return super().get_permission_names()

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        pk = self.kwargs.get("pk") or self.request.user.user_id
        context = super().get_context_data(**kwargs)
        context["groups"] = Groups.objects.filter(user_memberships__user_id=pk)

        return context


class History(LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    template_name = "user/history.html.dj"

    def get_permission_names(self) -> Any:
        pk = self.kwargs.get("pk")
        if pk != self.request.user.user_id:
            self.required_permissions = ("View Other User",)
        else:
            self.required_permissions = ()

        return super().get_permission_names()

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        pk = self.kwargs.get("pk") or self.request.user.user_id
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
