"""Atlas Collection views."""

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from index.models import (
    CollectionAttachments,
    CollectionChecklist,
    CollectionChecklistCompleted,
    CollectionComments,
    CollectionCommentStream,
    CollectionMilestoneTasks,
    CollectionMilestoneTasksCompleted,
    CollectionReports,
    Collections,
    CollectionTerms,
    Reports,
    Terms,
)


@login_required
def index(request):
    """Return main collection list."""
    # maintain compatibility with dotnet urls.
    if request.GET.get("id"):
        return redirect("/collections/%s" % request.GET.get("id"))

    context = {
        "permissions": request.user.get_permissions(),
        "user": request.user,
        "favorites": request.user.get_favorites(),
        "collections": Collections.objects.all().order_by("-_modified_at"),
        "title": "Collections",
    }

    return render(
        request,
        "collections.html.dj",
        context,
    )


@login_required
def item(request, collection_id):
    """Return specific collection."""
    try:
        collection = Collections.objects.get(collection_id=collection_id)
    except Collections.DoesNotExist:
        return redirect(index)

    context = {
        "permissions": request.user.get_permissions(),
        "user": request.user,
        "favorites": request.user.get_favorites(),
        "collection": collection,
        "title": collection.name,
        "favorite": "favorite"
        if request.user.has_favorite("collection", collection_id)
        else "",
    }

    return render(
        request,
        "collection.html.dj",
        context,
    )


@login_required
def edit(request, collection_id=None):
    """Save collection edits."""
    if request.method == "GET":
        return redirect(index)

    collection = (
        Collections.objects.get(collection_id=collection_id)
        if collection_id
        else Collections()
    )
    collection.name = request.POST.get("name", "")
    collection.purpose = request.POST.get("purpose", "")
    collection.description = request.POST.get("description", "")
    collection.ops_owner_id = request.POST.get("ops_owner_id")
    collection.exec_owner_id = request.POST.get("exec_owner_id")
    collection.analytics_owner_id = request.POST.get("analytics_owner_id")
    collection.data_owner_id = request.POST.get("data_owner_id")
    collection.financial_impact_id = request.POST.get("financial_impact_id")
    collection.strategic_importance_id = request.POST.get("strategic_importance_id")
    collection.external_documentation_url = request.POST.get(
        "external_documentation_url", ""
    )
    collection.hidden = "Y" if request.POST.get("hidden", "N") == "Y" else "N"
    collection.modified_by = request.user

    collection.save()

    return redirect(item, collection.collection_id)


@login_required
def reports_delete(request, collection_id, annotation_id):
    """Add or edit a collection report annotation."""
    CollectionReports.objects.filter(annotation_id=annotation_id).filter(
        collection_id=collection_id
    ).delete()

    collection = Collections.objects.get(collection_id=collection_id)

    return render(
        request, "collection_edit/current_reports.html.dj", {"collection": collection}
    )


@login_required
def reports(request, collection_id, annotation_id=None):
    """Add or edit a collection report annotation."""
    if request.method == "GET":
        return redirect(item, collection_id)

    data = json.loads(request.body.decode("UTF-8"))

    collection = Collections.objects.get(collection_id=collection_id)

    # validate report_id
    if not Reports.objects.filter(report_id=data.get("report_id")).exists():
        messages.error("Report does not exist.")
        return render(
            request,
            "collection_edit/current_reports.html.dj",
            {"collection": collection},
        )

    annotation = (
        CollectionReports.objects.get(annotation_id=annotation_id)
        if annotation_id
        else CollectionReports()
    )
    annotation.rank = (
        data.get("rank") if data.get("rank") and data.get("rank").isdigit() else None
    )
    annotation.annotation = data.get("annotation", "")
    annotation.report_id = data.get("report_id")
    annotation.collection_id = collection_id

    annotation.save()

    return render(
        request, "collection_edit/current_reports.html.dj", {"collection": collection}
    )


@login_required
def terms_delete(request, collection_id, annotation_id):
    """Add or edit a collection report annotation."""
    CollectionTerms.objects.filter(annotation_id=annotation_id).filter(
        collection_id=collection_id
    ).delete()

    collection = Collections.objects.get(collection_id=collection_id)

    return render(
        request, "collection_edit/current_reports.html.dj", {"collection": collection}
    )


@login_required
def terms(request, collection_id, annotation_id=None):
    """Add or edit a collection report annotation."""
    if request.method == "GET":
        return redirect(item, collection_id)

    data = json.loads(request.body.decode("UTF-8"))

    collection = Collections.objects.get(collection_id=collection_id)

    # validate term_id
    if not Terms.objects.filter(term_id=data.get("term_id")).exists():
        messages.error("Term does not exist.")
        return render(
            request, "collection_edit/current_terms.html.dj", {"collection": collection}
        )

    annotation = (
        CollectionTerms.objects.get(annotation_id=annotation_id)
        if annotation_id
        else CollectionTerms()
    )
    annotation.rank = (
        data.get("rank") if data.get("rank") and data.get("rank").isdigit() else None
    )
    annotation.annotation = data.get("annotation", "")
    annotation.term_id = data.get("term_id")
    annotation.collection_id = collection_id

    annotation.save()

    return render(
        request, "collection_edit/current_terms.html.dj", {"collection": collection}
    )


@login_required
def delete(request, collection_id):
    """Delete a collection.

    1. comments
    2. comment streams
    3. term and report annotations
    4. checklist tasks and completed tasks, and open checklists
    5. completed checklist
    6. attachments
    7. collection
    """
    CollectionComments.objects.filter(stream_id__collection_id=collection_id).delete()
    CollectionCommentStream.objects.filter(collection_id=collection_id).delete()

    CollectionTerms.objects.filter(collection_id=collection_id).delete()
    CollectionReports.objects.filter(collection_id=collection_id).delete()

    CollectionMilestoneTasksCompleted.objects.filter(
        collection_id=collection_id
    ).delete()

    CollectionChecklist.objects.filter(task__collection_id=collection_id).delete()
    CollectionMilestoneTasks.objects.filter(collection_id=collection_id).delete()

    CollectionChecklistCompleted.objects.filter(collection_id=collection_id).delete()

    CollectionAttachments.objects.filter(collection_id=collection_id).delete()

    Collections.objects.get(collection_id=collection_id).delete()

    return redirect(index)
