import io
from pathlib import Path

# @login_required
# def snippet(request,pk):
#     return "hello"
import regex as re
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from index.models import ReportComments, ReportDocs, ReportImages, Reports, Terms
from PIL import Image


@login_required
def index(request, pk):
    report_id = pk

    report = (
        Reports.objects.select_related("docs")
        .select_related("created_by")
        .select_related("modified_by")
        .select_related("docs__modified_by")
        .select_related("docs__created_by")
        .select_related("docs__requester")
        .select_related("docs__ops_owner")
        .select_related("type")
        .prefetch_related("queries")
        .prefetch_related("imgs")
        .prefetch_related("docs__logs")
        .prefetch_related("docs__logs__log")
        .prefetch_related("docs__logs__log__maintainer")
        .prefetch_related("docs__fragility_tags")
        .prefetch_related("docs__fragility_tags__fragility_tag")
        #   .prefetch_related("groups")
        #   .prefetch_related("groups__group")
        .prefetch_related("collections")
        .get(report_id=report_id)
    )

    parents = (
        Reports.objects.filter(parent__child=report_id)
        .exclude(type_id=12)
        .filter(visible="Y")
        .exclude(docs__hidden="Y")
        .prefetch_related("imgs")
        .order_by("name")
        .all()
    )

    children = (
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

    terms = Terms.objects.filter(
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

    return render(
        request,
        "report/one.html.dj",
        {
            "report_id": report_id,
            "report": report,
            "parents": parents,
            "children": children,
            # "favorite": favorite,
            "terms": terms,
        },
    )


@login_required
def profile(request, pk):
    report_id = pk
    return render(
        request,
        "report/report_profile.html.dj",
        {"maint_status": True},
    )


@login_required
def maint_status(request, pk):
    """Check report maintenance status.

    To be "past due":
        1. report maint schedule must not be 5
        2. must not have a maint log of 1 or 2 in the schedule interval

    """
    report_id = pk
    today = timezone.now()
    report = ReportDocs.objects.filter(report_id=report_id).exclude(
        maintenance_schedule__schedule_id=5
    )

    context = {"maint_status": False}

    if (
        not report.exists()
        or (report.exists() and not hasattr(report, "logs"))
        or (
            report.exists()
            and report.logs.filter(log__status__status_id__in=[1, 2]).exists()
        )
    ):
        return render(
            request,
            "report/sections/maint_status.html.dj",
            context,
        )

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

    return render(
        request,
        "report/sections/maint_status.html.dj",
        context,
    )


@login_required
def image(request, report_id, pk=None):
    image_format = "webp"

    # Browsers (IE11) that do not support webp
    if "HTTP_USER_AGENT" in request.META:
        user_agent = request.META["HTTP_USER_AGENT"].lower()
        if "trident" in user_agent or "msie" in user_agent:
            image_format = "jpeg"

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
        im = Image.open(io.BytesIO(img.image_data))
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

        hsize = int(float(im.size[1]) * float(max_ratio))
        wsize = int(float(im.size[0]) * float(max_ratio))

        out = im.resize((wsize, hsize))
        out = out.crop((0, 0, width, height))

        buf = io.BytesIO()
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

        hsize = int(float(im.size[1]) * float(max_ratio))
        wsize = int(float(im.size[0]) * float(max_ratio))

        out = im.resize((wsize, hsize))

        buf = io.BytesIO()
        out.save(buf, format=image_format)

        response = HttpResponse(buf.getvalue(), content_type="application/octet-stream")
        response["Content-Disposition"] = 'attachment; filename="{}.{}"'.format(
            pk,
            image_format,
        )

        return response

    response = HttpResponse(img.image_data, content_type="application/octet-stream")
    response["Content-Disposition"] = f'attachment; filename="{pk}_{wsize}x{hsize}.png"'

    return response
