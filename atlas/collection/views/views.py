"""Atlas Collection views."""

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView, View
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


class CollectionList(LoginRequiredMixin, ListView):
    queryset = Collections.objects.all().order_by("-_modified_at")
    context_object_name = "collections"
    template_name = "collections.html.dj"
    extra_context = {"title": "Collections"}

    def get(self, request, **kwargs):
        if request.GET.get("id"):
            return redirect("collection:item", pk=request.GET.get("id"))

        return super().get(request, **kwargs)


class CollectionDetails(LoginRequiredMixin, DetailView):
    template_name = "collection.html.dj"
    context_object_name = "collection"
    queryset = Collections.objects

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["favorite"] = (
            "favorite"
            if self.request.user.has_favorite("collection", self.kwargs["pk"])
            else ""
        )
        context["title"] = self.object.name

        return context

    def post(self, request, **kwargs):

        collection = Collections.objects.get(collection_id=self.kwargs["pk"])
        collection.name = request.POST.get("name", "")
        collection.search_summary = request.POST.get("search_summary", "")
        collection.description = request.POST.get("description", "")
        collection.hidden = "Y" if request.POST.get("hidden", "N") == "Y" else "N"
        collection.modified_by = request.user

        collection.save()

        return redirect(collection.get_absolute_url())


class CollectionNew(LoginRequiredMixin, View):
    def post(self, request):
        collection = Collections(
            name=request.POST.get("name", ""),
            search_summary=request.POST.get("search_summary", ""),
            description=request.POST.get("description", ""),
            hidden="Y" if request.POST.get("hidden", "N") == "Y" else "N",
            modified_by=request.user,
        )

        collection.save()

        return redirect(collection.get_absolute_url())

    def get(self, request):
        return redirect("collection:list")


@login_required
def reports_delete(request, pk, annotation_id):
    """Add or edit a collection report annotation."""
    CollectionReports.objects.filter(annotation_id=annotation_id).filter(
        collection_id=pk
    ).delete()

    collection = get_object_or_404(Collections, pk=pk)

    return render(
        request, "collection_edit/current_reports.html.dj", {"collection": collection}
    )


@login_required
def reports(request, pk, annotation_id=None):
    """Add or edit a collection report annotation."""
    if request.method == "GET":
        return redirect("collection:item", pk=pk)

    data = json.loads(request.body.decode("UTF-8"))

    collection = get_object_or_404(Collections, pk=pk)

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
def delete(request, pk):
    """Delete a collection.

    1. comments
    2. comment streams
    3. term and report annotations
    4. checklist tasks and completed tasks, and open checklists
    5. completed checklist
    6. attachments
    7. collection
    """
    CollectionComments.objects.filter(stream_id__collection_id=pk).delete()
    CollectionCommentStream.objects.filter(collection_id=pk).delete()

    CollectionTerms.objects.filter(collection_id=pk).delete()
    CollectionReports.objects.filter(collection_id=pk).delete()

    CollectionMilestoneTasksCompleted.objects.filter(collection_id=pk).delete()

    CollectionChecklist.objects.filter(task__collection_id=pk).delete()
    CollectionMilestoneTasks.objects.filter(collection_id=pk).delete()

    CollectionChecklistCompleted.objects.filter(collection_id=pk).delete()

    CollectionAttachments.objects.filter(collection_id=pk).delete()

    get_object_or_404(Collections, pk=pk).delete()

    return redirect("collection:list")
