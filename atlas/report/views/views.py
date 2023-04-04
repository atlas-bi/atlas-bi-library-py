"""Django views for Atlas Reports."""
# pylint: disable=C0115, C0116, W0613, R0912, R0914, R0915
import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import regex as re
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils import timezone
from django.views.generic import DetailView, TemplateView, UpdateView, View
from index.models import (
    CollectionReports,
    Collections,
    MaintenanceLogs,
    ReportAttachments,
    ReportDocs,
    ReportFragilityTags,
    ReportImages,
    ReportQueries,
    Reports,
    ReportTerms,
    ReportTickets,
    Terms,
)
from PIL import Image
from report.templatetags.url_tags import run_authorization

from atlas.decorators import NeverCacheMixin, PermissionsCheckMixin


class Attachment(LoginRequiredMixin, View):
    def get(
        self, request: HttpRequest, *args: Tuple[Any], **kwargs: Dict[Any, Any]
    ) -> HttpResponse:
        pk = self.kwargs["pk"]

        attachment = (
            ReportAttachments.objects.filter(attachment_id=pk)
            .select_related("report", "report__type")
            .first()
        )

        if run_authorization(attachment.report, request):
            response = HttpResponse("", status=302)
            response["Location"] = f"file:{attachment.path}"
            return response
            # return HttpResponseRedirect(attachment.path)

        return redirect(
            reverse("report:item", kwargs={"pk": attachment.report_id})
            + "?error=You are not authorized to view that report."
        )


class ReportDetails(LoginRequiredMixin, DetailView):
    template_name = "report/one.html.dj"
    context_object_name = "report"

    queryset = (
        Reports.objects.select_related("docs")
        .select_related("created_by")
        .select_related("modified_by")
        .select_related("docs__modified_by")
        .select_related("docs__created_by")
        .select_related("docs__requester")
        .select_related("docs__ops_owner")
        .select_related("type")
        .prefetch_related("queries")
        .prefetch_related("starred")
        .prefetch_related(Prefetch("imgs", ReportImages.objects.order_by("rank")))
        .prefetch_related("docs__maintenance_logs")
        .prefetch_related("docs__maintenance_logs__maintainer")
        .prefetch_related("docs__fragility_tags")
        .prefetch_related("docs__fragility")
        .prefetch_related("docs__frequency")
        .prefetch_related("docs__maintenance_schedule")
        .prefetch_related("docs__fragility_tags__fragility_tag")
        .prefetch_related("docs__tickets")
        .prefetch_related("tags__tag")
        .prefetch_related("groups")
        .prefetch_related("groups__group")
        .prefetch_related(
            Prefetch("collections", CollectionReports.objects.order_by("rank"))
        )
    )

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        """Add additional items to the context."""
        context = super().get_context_data(**kwargs)

        report_id = self.kwargs["pk"]

        context["parents"] = (
            Reports.objects.filter(parent__child=report_id)
            .exclude(type_id=12)
            .filter(visible="Y")
            .exclude(docs__hidden="Y")
            .prefetch_related("imgs")
            .order_by("name")
            .all()
        )

        context["children"] = (
            Reports.objects.filter(child__parent=report_id)
            .exclude(system_identifier="IDK")
            .filter(visible="Y")
            .exclude(docs__hidden="Y")
            .prefetch_related("imgs")
            .order_by("name")
            .all()
        )
        # not listing grandchildren yet.

        # favorite = "yes" if request.user.has_favorite("report", report_id) else "no"
        context["component_queries"] = ReportQueries.objects.filter(query_id=-1)
        context["collections"] = Collections.objects.filter(collection_id=-1)
        context["terms"] = Terms.objects.filter(
            report_docs__report_doc__report__report_id=report_id
        ).all()

        # var report_terms = await (from r in _context.ReportObjectDocTerms
        #                           where r.ReportObjectId == id
        #                           select new
        #                           {
        #                               Name = r.Term.Name,
        #                               Id = r.TermId,
        #                               Summary = r.Term.Summary,
        #                               Definition = r.Term.TechnicalDefinition,
        #                           }).ToListAsync();

        # var child_report_terms = await ( // child terms
        #                     from c in _context.ReportObjectHierarchies
        #                     where c.ParentReportObjectId == id
        #                     join r in _context.ReportObjectDocTerms on c.ChildReportObjectId equals r.ReportObjectId
        #                     select new
        #                     {
        #                         Name = r.Term.Name,
        #                         Id = r.TermId,
        #                         Summary = r.Term.Summary,
        #                         Definition = r.Term.TechnicalDefinition,
        #                     }).ToListAsync();

        # var grandchild_report_terms = await (from c in _context.ReportObjectHierarchies
        #                                      where c.ParentReportObjectId == id
        #                                      join gc in _context.ReportObjectHierarchies on c.ChildReportObjectId equals gc.ParentReportObjectId
        #                                      join r in _context.ReportObjectDocTerms on gc.ChildReportObjectId equals r.ReportObjectId
        #                                      select new
        #                                      {
        #                                          Name = r.Term.Name,
        #                                          Id = r.TermId,
        #                                          Summary = r.Term.Summary,
        #                                          Definition = r.Term.TechnicalDefinition,
        #                                      }).ToListAsync();

        # var great_grandchild_report_terms = await (from c in _context.ReportObjectHierarchies
        #                                            where c.ParentReportObjectId == id
        #                                            join gc in _context.ReportObjectHierarchies on c.ChildReportObjectId equals gc.ParentReportObjectId
        #                                            join ggc in _context.ReportObjectHierarchies on gc.ChildReportObjectId equals ggc.ParentReportObjectId
        #                                            join r in _context.ReportObjectDocTerms on ggc.ChildReportObjectId equals r.ReportObjectId
        #                                            select new
        #                                            {
        #                                                Name = r.Term.Name,
        #                                                Id = r.TermId,
        #                                                Summary = r.Term.Summary,
        #                                                Definition = r.Term.TechnicalDefinition,
        #                                            }).ToListAsync();

        context["title"] = self.object
        return context


class ReportEdit(
    NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, UpdateView
):
    required_permissions = ("Edit Report Documentation",)
    template_name = "report/edit.html.dj"
    context_object_name = "report_doc"
    queryset = (
        ReportDocs.objects.select_related("requester")
        .select_related("ops_owner")
        .select_related("frequency")
        .select_related("maintenance_schedule")
        .select_related("fragility")
        .prefetch_related(
            Prefetch("report__imgs", ReportImages.objects.order_by("rank"))
        )
        .prefetch_related("maintenance_logs")
        .prefetch_related("maintenance_logs__maintainer")
        .prefetch_related("fragility_tags")
        .prefetch_related("fragility_tags__fragility_tag")
        .prefetch_related("tickets")
        .prefetch_related(
            Prefetch("report__collections", CollectionReports.objects.order_by("rank"))
        )
    )
    fields: List[str] = []

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = f"Editing {self.object.report}"

        return context

    def post(
        self, request: HttpRequest, *args: Tuple[Any], **kwargs: Dict[Any, Any]
    ) -> HttpResponse:
        report_doc, _ = ReportDocs.objects.get_or_create(report_id=self.kwargs["pk"])

        report_doc.description = request.POST.get("description", "")
        report_doc.assumptions = request.POST.get("assumptions", "")

        report_doc.ops_owner_id = request.POST.get("ops_owner_id", "")
        report_doc.requester_id = request.POST.get("requester_id", "")
        report_doc.external_url = request.POST.get("external_url", "")

        report_doc.org_value_id = request.POST.get("org_value_id", "")
        report_doc.frequency_id = request.POST.get("frequency_id", "")
        report_doc.fragility_id = request.POST.get("fragility_id", "")
        report_doc.maintenance_schedule_id = request.POST.get(
            "maintenance_schedule_id", ""
        )

        report_doc.executive_report = request.POST.get("executive_report", "N")
        report_doc.do_not_purge = request.POST.get("do_not_purge", "N")
        report_doc.hidden = request.POST.get("hidden", "N")

        report_doc.save()

        # remove old linked fragility tags.
        ReportFragilityTags.objects.filter(report_doc=report_doc).delete()

        # add new tags
        for fragility_tag_id in request.POST.getlist("fragility_tag_id"):
            ReportFragilityTags(
                report_doc=report_doc, fragility_tag_id=fragility_tag_id
            ).save()

        # remove old linked collections.
        CollectionReports.objects.filter(report_id=report_doc.report_id).delete()

        # add new collections
        for rank, collection_id in enumerate(request.POST.getlist("collection_id")):
            CollectionReports(
                collection_id=collection_id, report_id=report_doc.report_id, rank=rank
            ).save()

        # remove old linked terms.
        ReportTerms.objects.filter(report_doc=report_doc).delete()

        # add new terms.
        for term_id in request.POST.getlist("term_id"):
            ReportTerms(report_doc=report_doc, term_id=term_id).save()

        # remove removed images
        image_list = request.POST.getlist("image_id")
        ReportImages.objects.filter(report_id=report_doc.report_id).exclude(
            image_id__in=image_list
        ).delete()

        # update image rank
        for rank, image_id in enumerate(image_list):
            ReportImages.objects.update_or_create(
                report_id=report_doc.report_id,
                image_id=image_id,
                defaults={"rank": rank},
            )

        # add maintenance log
        if request.POST.get("maintenance_status_id"):
            MaintenanceLogs(
                maintainer=request.user,
                comments=request.POST.get("maintenance_comments", ""),
                status_id=request.POST.get("maintenance_status_id"),
                report_id=report_doc.report_id,
            ).save()

        # removed removed tickets
        ticket_list = request.POST.getlist("ticket_id")
        ReportTickets.objects.filter(report_doc=report_doc).exclude(
            ticket_id__in=ticket_list
        ).delete()

        # add new ticket
        if request.POST.get("ticket_number"):
            ReportTickets(
                number=request.POST.get("ticket_number"),
                description=request.POST.get("ticket_description"),
                report_doc=report_doc,
                url=request.POST.get("ticket_url"),
            ).save()

        return redirect(
            report_doc.report.get_absolute_url() + "?success=Changes saved."
        )


@login_required
def profile(request: HttpRequest, pk: int) -> HttpResponse:
    # report_id = pk
    return render(
        request,
        "report/report_profile.html.dj",
        {"maint_status": True},
    )


class MaintenanceStatus(
    NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, TemplateView
):
    """Check report maintenance status.

    To be "past due":
        1. report maint schedule must not be 5
        2. must not have a maint log of 1 or 2 in the schedule interval

    """

    template_name = "report/sections/maint_status.html.dj"
    required_permissions = ("Edit Report Documentation",)

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        context = super().get_context_data(**kwargs)
        report_id = self.kwargs["pk"]
        today = timezone.now()
        report = ReportDocs.objects.filter(report_id=report_id).exclude(
            maintenance_schedule__schedule_id=5
        )

        context["maint_status"] = False

        if (
            not report.exists()
            or (report.exists() and not hasattr(report, "logs"))
            or (
                report.exists()
                and report.logs.filter(log__status__status_id__in=[1, 2]).exists()
            )
        ):
            return context

        report = report.first()

        last_maintained = (
            report.logs.filter(log__status__status_id__in=[1, 2])
            .latest("log__maintained_at")
            .log.maintained_at
        )

        maint_lookup = {
            # quarterly
            1: last_maintained + relativedelta(months=3),
            # semi-yearly
            2: last_maintained + relativedelta(months=6),
            # yearly
            3: last_maintained + relativedelta(years=1),
            # bi-yearly
            4: last_maintained + relativedelta(years=2),
        }

        # lookup, otherwise past due
        next_date = maint_lookup.get(report.maintenance_schedule_id, last_maintained)

        if next_date <= today:
            context["maint_status"] = True

        return context


@login_required
def image(
    request: HttpRequest, report_id: int, pk: Optional[Union[int, str]] = None
) -> HttpResponse:
    if request.method == "POST":
        if request.FILES["File"].content_type not in [
            "image/jpeg",
            "image/png",
            "image/gif",
        ]:
            return JsonResponse({"error": "Image must be a jpeg, png or gig."})

        if request.FILES["File"].size > 1024 * 1024:  # 1mb max
            return JsonResponse({"error": "Image must be less than 1MB."})

        data = request.FILES["File"].file.read()
        new_image = ReportImages(report_id=report_id, data=data, rank=-1)
        new_image.save()

        return JsonResponse({"image_id": new_image.image_id})

    image_format = request.GET.get("format", "webp")

    # Browsers (IE11) that do not support webp
    # if "HTTP_USER_AGENT" in request.META:
    #     user_agent = request.META.get("HTTP_USER_AGENT").lower()
    #     if "trident" in user_agent or "msie" in user_agent:
    #         image_format = "jpeg"

    size = request.GET.get("size", "")

    if pk:
        img = get_object_or_404(ReportImages, report_id=report_id, image_id=pk)
    else:
        img = ReportImages.objects.filter(report_id=report_id)
        if img.exists():
            img = img.first()
        else:
            img = None

    if img:
        im = Image.open(io.BytesIO(img.data))
        pk = img.pk
    else:
        im = Image.open(
            Path(__file__).parent.parent.parent / "static/img/report_placeholder.png"
        )
        pk = "report_placeholder"

    if re.match(r"^\d+x\d+$", size):
        width, height = (int(x) for x in size.split("x"))

        # image must be a perfect ratio, without distortion.
        # first resize close to size, then crop

        max_ratio = max((width / float(im.size[0])), (height / float(im.size[1])))
        out = im
        if max_ratio < 1:
            hsize = int(float(im.size[1]) * float(max_ratio))
            wsize = int(float(im.size[0]) * float(max_ratio))

            out = im.resize((wsize, hsize))
            # out = out.crop((0, 0, width, height))

        buf = io.BytesIO()
        if image_format == "jpeg":
            out = out.convert("RGB")
        out.save(buf, format=image_format)

        response = HttpResponse(buf.getvalue(), content_type="application/octet-stream")
        response[
            "Content-Disposition"
        ] = f'attachment; filename="{pk}_{width}x{height}.{image_format}"'

        return response

    # if only a width is specified
    if re.match(r"^\d+x_$", size):
        width = int(size.split("x")[0])

        max_ratio = width / float(im.size[0])
        out = im
        if max_ratio < 1:
            hsize = int(float(im.size[1]) * float(max_ratio))
            wsize = int(float(im.size[0]) * float(max_ratio))

            out = im.resize((wsize, hsize))

        buf = io.BytesIO()
        if image_format == "jpeg":
            out = out.convert("RGB")
        out.save(buf, format=image_format)

        response = HttpResponse(buf.getvalue(), content_type="application/octet-stream")
        response["Content-Disposition"] = f'attachment; filename="{pk}.{image_format}"'

        return response

    response = HttpResponse(img.data, content_type="application/octet-stream")
    response["Content-Disposition"] = f'attachment; filename="{pk}_{size}.png"'

    return response
