"""Atlas Group views."""

from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from index.models import Groups

from atlas.decorators import PermissionsCheckMixin


class GroupDetails(LoginRequiredMixin, PermissionsCheckMixin, DetailView):
    required_permissions = ("View Groups",)
    template_name = "group/index.html.dj"
    context_object_name = "group"
    queryset = Groups.objects.prefetch_related(
        "user_memberships", "user_memberships__user"
    ).prefetch_related("starred")

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        """Add additional items to the context."""
        context = super().get_context_data(**kwargs)

        context["title"] = self.object

        return context
