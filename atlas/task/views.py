"""Atlas tasks."""
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max, Q, Sum
from django.utils import timezone
from django.views.generic import ListView, TemplateView
from index.models import MaintenanceLogs, Reports

from atlas.decorators import NeverCacheMixin


class Index(NeverCacheMixin, LoginRequiredMixin, TemplateView):
    template_name = "task/index.html.dj"
    extra_context = {"title": "Tasks"}


class RecommendRetire(NeverCacheMixin, LoginRequiredMixin, ListView):
    template_name = "task/recommend_retire.html.dj"
    queryset = (
        MaintenanceLogs.objects.filter(status__name="Recommend Retire")
        .exclude(report_doc__hidden="Y")
        .exclude(report_doc__report__visible="N")
        .select_related("report_doc__report")
    )
    context_object_name = "reports"


class Unused(NeverCacheMixin, LoginRequiredMixin, ListView):
    template_name = "task/unused.html.dj"
    two_months_ago = timezone.now() + timedelta(days=-62)
    queryset = (
        Reports.objects.filter(
            type__visible="Y",
            visible="Y",
            runs__isnull=True,
            modified_at__lte=two_months_ago,
        )
        .exclude(orphan="Y")
        .select_related("type")
        .select_related("modified_by")
    )
    context_object_name = "reports"


class MaintenanceRequired(NeverCacheMixin, LoginRequiredMixin, ListView):
    template_name = "task/maintenance_required.html.dj"

    maint_window = timedelta(days=62)

    two_years_ago = timezone.now() + timedelta(days=-730) + maint_window
    one_year_ago = timezone.now() + timedelta(days=-365) + maint_window
    one_quarter_ago = timezone.now() + timedelta(days=-92) + maint_window
    six_months_ago = timezone.now() + timedelta(days=-183) + maint_window

    queryset = (
        Reports.objects.filter(visible="Y")
        .exclude(orphan="Y")
        .exclude(
            docs__maintenance_schedule_id=5, docs__maintenance_schedule__isnull=True
        )
        .filter(
            Q(docs__maintenance_schedule_id=2)
            & (
                Q(docs__maintenance_logs__maintained_at__lte=six_months_ago)
                | Q(docs__maintenance_logs__isnull=True)
            )
        )
        .filter(
            Q(docs__maintenance_schedule_id=1)
            & (
                Q(docs__maintenance_logs__maintained_at__lte=one_quarter_ago)
                | Q(docs__maintenance_logs__isnull=True)
            )
        )
        .filter(
            Q(docs__maintenance_schedule_id=3)
            & (
                Q(docs__maintenance_logs__maintained_at__lte=one_year_ago)
                | Q(docs__maintenance_logs__isnull=True)
            )
        )
        .filter(
            Q(docs__maintenance_schedule_id=4)
            & (
                Q(docs__maintenance_logs__maintained_at__lte=two_years_ago)
                | Q(docs__maintenance_logs__isnull=True)
            )
        )
        .select_related("modified_by")
    )

    context_object_name = "reports"


class AuditOnly(NeverCacheMixin, LoginRequiredMixin, ListView):
    template_name = "task/audit_only.html.dj"

    queryset = (
        Reports.objects.filter(visible="Y", docs__maintenance_schedule_id=5)
        .exclude(orphan="Y")
        .select_related("modified_by")
    )

    context_object_name = "reports"


class NoSchedule(NeverCacheMixin, LoginRequiredMixin, ListView):
    template_name = "task/no_schedule.html.dj"

    queryset = (
        Reports.objects.filter(visible="Y", docs__maintenance_schedule_id__isnull=True)
        .exclude(orphan="Y")
        .exclude(docs__isnull=True)
        .select_related("modified_by")
    )

    context_object_name = "reports"


class NotAnalytics(NeverCacheMixin, LoginRequiredMixin, ListView):
    template_name = "task/not_analytics.html.dj"
    six_months_ago = timezone.now() + timedelta(days=-183)
    queryset = (
        Reports.objects.filter(visible="Y", modified_at__gte=six_months_ago)
        .exclude(orphan="Y")
        .exclude(modified_by__group_links__group__name="Analytics (group)")
        .select_related("modified_by", "type")
        .order_by("-modified_at")
    )

    context_object_name = "reports"


class TopUndocumented(NeverCacheMixin, LoginRequiredMixin, ListView):
    template_name = "task/top_undocumented.html.dj"
    queryset = (
        Reports.objects.filter(visible="Y", docs__isnull=True, type__visible="Y")
        .exclude(orphan="Y")
        .exclude(runs__isnull=True)
        .select_related("modified_by", "type")
        .annotate(
            total_runs=Sum("runs__runs"), last_run=Max("runs__run__runstarttime_day")
        )
        .filter(total_runs__gte=0)
        .order_by("-total_runs")
    )

    context_object_name = "reports"


class NewUndocumented(NeverCacheMixin, LoginRequiredMixin, ListView):
    template_name = "task/new_undocumented.html.dj"

    queryset = (
        Reports.objects.filter(visible="Y", docs__isnull=True, type__visible="Y")
        .exclude(orphan="Y")
        .select_related("modified_by", "type")
        .order_by("-modified_at")
    )

    context_object_name = "reports"
