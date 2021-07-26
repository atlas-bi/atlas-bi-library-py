"""Atlas Project views."""

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from index.models import (
    ProjectAttachments,
    ProjectChecklist,
    ProjectChecklistCompleted,
    ProjectComments,
    ProjectCommentStream,
    ProjectMilestoneTasks,
    ProjectMilestoneTasksCompleted,
    ProjectReports,
    Projects,
    ProjectTerms,
    Reports,
    Terms,
)


@login_required
def index(request):
    """Return main project list."""
    # maintain compatibility with dotnet urls.
    if request.GET.get("id"):
        return redirect("/projects/%s" % request.GET.get("id"))

    context = {
        "permissions": request.user.get_permissions(),
        "user": request.user,
        "favorites": request.user.get_favorites(),
        "projects": Projects.objects.all().order_by("-_modified_at"),
        "title": "Projects",
    }

    return render(
        request,
        "projects.html.dj",
        context,
    )


@login_required
def item(request, project_id):
    """Return specific project."""
    try:
        project = Projects.objects.get(project_id=project_id)
    except Projects.DoesNotExist:
        return redirect(index)

    context = {
        "permissions": request.user.get_permissions(),
        "user": request.user,
        "favorites": request.user.get_favorites(),
        "project": project,
        "title": project.name,
        "favorite": "favorite"
        if request.user.has_favorite("project", project_id)
        else "",
    }

    return render(
        request,
        "project.html.dj",
        context,
    )


@login_required
def edit(request, project_id=None):
    """Save project edits."""
    if request.method == "GET":
        return redirect(index)

    project = Projects.objects.get(project_id=project_id) if project_id else Projects()
    project.name = request.POST.get("name", "")
    project.purpose = request.POST.get("purpose", "")
    project.description = request.POST.get("description", "")
    project.ops_owner_id = request.POST.get("ops_owner_id")
    project.exec_owner_id = request.POST.get("exec_owner_id")
    project.analytics_owner_id = request.POST.get("analytics_owner_id")
    project.data_owner_id = request.POST.get("data_owner_id")
    project.financial_impact_id = request.POST.get("financial_impact_id")
    project.strategic_importance_id = request.POST.get("strategic_importance_id")
    project.external_documentation_url = request.POST.get(
        "external_documentation_url", ""
    )
    project.hidden = "Y" if request.POST.get("hidden", "N") == "Y" else "N"
    project.modified_by = request.user

    project.save()

    return redirect(item, project.project_id)


@login_required
def reports_delete(request, project_id, annotation_id):
    """Add or edit a project report annotation."""
    ProjectReports.objects.filter(annotation_id=annotation_id).filter(
        project_id=project_id
    ).delete()

    project = Projects.objects.get(project_id=project_id)

    return render(request, "project_edit/current_reports.html.dj", {"project": project})


@login_required
def reports(request, project_id, annotation_id=None):
    """Add or edit a project report annotation."""
    if request.method == "GET":
        return redirect(item, project_id)

    data = json.loads(request.body.decode("UTF-8"))

    project = Projects.objects.get(project_id=project_id)

    # validate report_id
    if not Reports.objects.filter(report_id=data.get("report_id")).exists():
        messages.error("Report does not exist.")
        return render(
            request, "project_edit/current_reports.html.dj", {"project": project}
        )

    annotation = (
        ProjectReports.objects.get(annotation_id=annotation_id)
        if annotation_id
        else ProjectReports()
    )
    annotation.rank = (
        data.get("rank") if data.get("rank") and data.get("rank").isdigit() else None
    )
    annotation.annotation = data.get("annotation", "")
    annotation.report_id = data.get("report_id")
    annotation.project_id = project_id

    annotation.save()

    return render(request, "project_edit/current_reports.html.dj", {"project": project})


@login_required
def terms_delete(request, project_id, annotation_id):
    """Add or edit a project report annotation."""
    ProjectTerms.objects.filter(annotation_id=annotation_id).filter(
        project_id=project_id
    ).delete()

    project = Projects.objects.get(project_id=project_id)

    return render(request, "project_edit/current_reports.html.dj", {"project": project})


@login_required
def terms(request, project_id, annotation_id=None):
    """Add or edit a project report annotation."""
    if request.method == "GET":
        return redirect(item, project_id)

    data = json.loads(request.body.decode("UTF-8"))

    project = Projects.objects.get(project_id=project_id)

    # validate term_id
    if not Terms.objects.filter(term_id=data.get("term_id")).exists():
        messages.error("Term does not exist.")
        return render(
            request, "project_edit/current_terms.html.dj", {"project": project}
        )

    annotation = (
        ProjectTerms.objects.get(annotation_id=annotation_id)
        if annotation_id
        else ProjectTerms()
    )
    annotation.rank = (
        data.get("rank") if data.get("rank") and data.get("rank").isdigit() else None
    )
    annotation.annotation = data.get("annotation", "")
    annotation.term_id = data.get("term_id")
    annotation.project_id = project_id

    annotation.save()

    return render(request, "project_edit/current_terms.html.dj", {"project": project})


@login_required
def delete(request, project_id):
    """Delete a project.

    1. comments
    2. comment streams
    3. term and report annotations
    4. checklist tasks and completed tasks, and open checklists
    5. completed checklist
    6. attachments
    7. project
    """
    ProjectComments.objects.filter(stream_id__project_id=project_id).delete()
    ProjectCommentStream.objects.filter(project_id=project_id).delete()

    ProjectTerms.objects.filter(project_id=project_id).delete()
    ProjectReports.objects.filter(project_id=project_id).delete()

    ProjectMilestoneTasksCompleted.objects.filter(project_id=project_id).delete()

    ProjectChecklist.objects.filter(task__project_id=project_id).delete()
    ProjectMilestoneTasks.objects.filter(project_id=project_id).delete()

    ProjectChecklistCompleted.objects.filter(project_id=project_id).delete()

    ProjectAttachments.objects.filter(project_id=project_id).delete()

    Projects.objects.get(project_id=project_id).delete()

    return redirect(index)
