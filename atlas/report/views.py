from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from index.models import ReportComments, ReportDocs, ReportImages, Reports, Terms


@login_required
def index(request, report_id):

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
        .prefetch_related("groups")
        .prefetch_related("groups__group")
        .prefetch_related("projects")
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

    favorite = "yes" if request.user.has_favorite("report", report_id) else "no"

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
        "report.html.dj",
        {
            "permissions": request.user.get_permissions(),
            "report_id": report_id,
            "report": report,
            "parents": parents,
            "children": children,
            "favorite": favorite,
            "user": request.user,
            "terms": terms,
            "favorites": request.user.get_favorites(),
        },
    )


@login_required
def profile(request, report_id):
    return render(
        request,
        "report_profile.html.dj",
        {"maint_status": True},
    )


@login_required
def maint_status(request, report_id):
    """Check report maintenance status.

    To be "past due":
        1. report maint schedule must not be 5
        2. must not have a maint log of 1 or 2 in the schedule interval

    """
    today = timezone.now()
    report = ReportDocs.objects.filter(report_id=report_id).exclude(
        maintenance_schedule__schedule_id=5
    )

    past_due = False

    if report.exists():

        report = report.first()
        next_date = today
        if report.logs.filter(log__status__status_id__in=[1, 2]).exists():

            last_maintained = (
                report.logs.filter(log__status__status_id__in=[1, 2])
                .latest("log__maintained_at")
                .log.maintained_at
            )

            # quarterly
            if report.maintenance_schedule_id == 1:
                next_date = last_maintained + relativedelta(months=3)
            # semi-yearly
            elif report.maintenance_schedule_id == 2:
                next_date = last_maintained + relativedelta(months=6)
            # yearly
            elif report.maintenance_schedule_id == 3:
                next_date = last_maintained + relativedelta(years=1)
            # bi-yearly
            elif report.maintenance_schedule_id == 4:
                next_date = last_maintained + relativedelta(years=2)
            # otherwise.. past due
            else:
                next_date = last_maintained

        if next_date <= today:
            past_due = True

    return render(
        request,
        "sections/maint_status.html.dj",
        {"maint_status": past_due},
    )


@login_required
def image(request, report_id, image_id):

    img = ReportImages.objects.get(report_id=report_id, image_id=image_id)

    response = HttpResponse(img.image_data, content_type="application/octet-stream")
    response["Content-Disposition"] = 'attachment; filename="%s.png"' % img.image_id

    return response


@never_cache
@login_required
def comments(request, report_id):
    """Return term comments."""
    report_comments = (
        ReportComments.objects.filter(stream_id__report_id=report_id)
        .order_by("-stream_id", "comment_id")
        .all()
    )
    context = {
        "permissions": request.user.get_permissions(),
        "comments": report_comments,
    }
    return render(
        request,
        "report_comments.html.dj",
        context,
    )
