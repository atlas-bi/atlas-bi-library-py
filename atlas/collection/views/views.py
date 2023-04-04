"""Atlas Collection views."""
# pylint: disable=C0116,C0115,W0613,W0212,R0201

import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, View
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
    template_name = "collection/all.html.dj"
    extra_context = {"title": "Collections"}

    def get(self, request, **kwargs):
        if request.GET.get("id"):
            return redirect("collection:item", pk=request.GET.get("id"))

        return super().get(request, **kwargs)


class CollectionDetails(LoginRequiredMixin, DetailView):
    template_name = "collection/one.html.dj"
    context_object_name = "collection"
    queryset = Collections.objects

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context["favorite"] = (
        #     "favorite"
        #     if self.request.user.has_favorite("collection", self.kwargs["pk"])
        #     else ""
        # )
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


class CollectionDelete(LoginRequiredMixin, DeleteView):
    model = Collections
    success_url = reverse_lazy("collection:list")

    def post(self, *args, **kwargs):
        pk = self.kwargs["pk"]

        CollectionComments.objects.filter(stream_id__collection_id=pk).delete()
        CollectionCommentStream.objects.filter(collection_id=pk).delete()

        CollectionTerms.objects.filter(collection_id=pk).delete()
        CollectionReports.objects.filter(collection_id=pk).delete()

        CollectionMilestoneTasksCompleted.objects.filter(collection_id=pk).delete()

        CollectionChecklist.objects.filter(task__collection_id=pk).delete()
        CollectionMilestoneTasks.objects.filter(collection_id=pk).delete()

        CollectionChecklistCompleted.objects.filter(collection_id=pk).delete()

        CollectionAttachments.objects.filter(collection_id=pk).delete()

        return super().post(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class ReportLinkDelete(LoginRequiredMixin, DeleteView):
    model = CollectionReports

    def get_success_url(self):
        return reverse_lazy(
            "collection:reports", kwargs={"collection_id": self.kwargs["collection_id"]}
        )

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class ReportLinkNew(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        reportlinks = CollectionReports.objects.filter(
            collection_id=self.kwargs["collection_id"]
        )

        return render(
            self.request,
            "collection/edit/current_reports.html.dj",
            {"reportlinks": reportlinks},
        )

    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("UTF-8"))

        if Reports.objects.filter(report_id=data.get("report_id")).exists():
            CollectionReports.objects.update_or_create(
                defaults={
                    "rank": data.get("rank")
                    if data.get("rank") and str(data.get("rank")).isdigit()
                    else None
                },
                report_id=data.get("report_id"),
                collection_id=self.kwargs["collection_id"],
            )

        else:
            messages.error(self.request, "Report does not exist.")

        return self.get(*args, **kwargs)


class TermLinkDelete(LoginRequiredMixin, DeleteView):
    model = CollectionTerms

    def get_success_url(self):
        return reverse(
            "collection:terms", kwargs={"collection_id": self.kwargs["collection_id"]}
        )

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class TermLinkNew(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        termlinks = CollectionTerms.objects.filter(
            collection_id=self.kwargs["collection_id"]
        )

        return render(
            self.request,
            "collection/edit/current_terms.html.dj",
            {"termlinks": termlinks},
        )

    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("UTF-8"))

        if Terms.objects.filter(term_id=data.get("term_id")).exists():
            CollectionTerms.objects.update_or_create(
                defaults={
                    "rank": data.get("rank")
                    if data.get("rank") and str(data.get("rank")).isdigit()
                    else None
                },
                term_id=data.get("term_id"),
                collection_id=self.kwargs["collection_id"],
            )

        else:
            messages.error(self.request, "Term does not exist.")

        return self.get(*args, **kwargs)
