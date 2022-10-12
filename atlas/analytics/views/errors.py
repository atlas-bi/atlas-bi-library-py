"""Atlas analytics views."""

from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import TemplateView
from index.models import AnalyticsErrors, Groups, Users

from atlas.decorators import NeverCacheMixin, PermissionsCheckMixin


class Index(NeverCacheMixin, LoginRequiredMixin, TemplateView, PermissionsCheckMixin):
    template_name = "analytics/errors.html.dj"
    required_permissions = ("View Site Analytics",)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        page = int(self.request.GET.get("page", 1))
        start_at = int(self.request.GET.get("start_at", -86400))
        end_at = int(self.request.GET.get("end_at", 0))
        user_id = self.request.GET.get("user_id", -1)
        group_id = self.request.GET.get("group_id", -1)
        page_size = 10

        now = timezone.now()
        start_absolute = now + timedelta(seconds=start_at)
        end_absolute = now + timedelta(seconds=end_at)

        errors = AnalyticsErrors.objects.filter(
            access_date__gte=start_absolute, access_date__lte=end_absolute
        )

        if user_id > 0 and Users.objects.filter(user_id=user_id).exists():
            errors = errors.filter(user_id=user_id)

        if group_id > 0 and Groups.objects.filter(group_id=group_id).exists():
            errors = errors.filter(user__group__id=group_id)

        errors = errors.order_by("-update_time").all()
        paginator = Paginator(errors, page_size)

        context["unresolved"] = len(errors.exclude(handled=1))
        context["errors"] = paginator.get_page(page)

        return context

    def post(self, request, *args, **kwargs):
        error = AnalyticsErrors.objects.filter(pk=self.kwargs["pk"])
        if error.exists():
            error = error.first()
            if error.handled == 1:
                error.handled = None
            else:
                error.handled = 1

            error.save()
            return HttpResponse("Changes saved.", content_type="text/plain")
        return HttpResponse("No changes to save.", content_type="text/plain")
