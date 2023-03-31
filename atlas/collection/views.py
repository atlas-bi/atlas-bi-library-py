"""Atlas Collection views."""
# pylint: disable=C0116,C0115,W0613,W0212

from typing import Any, Dict, List, Tuple

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.views.generic import (
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
from index.models import CollectionReports, Collections, CollectionTerms

from atlas.decorators import NeverCacheMixin, PermissionsCheckMixin


class CollectionList(LoginRequiredMixin, ListView):
    queryset = (
        Collections.objects.prefetch_related("starred").all().order_by("-modified_at")
    )
    context_object_name = "collections"
    template_name = "collection/all.html.dj"
    extra_context = {"title": "Collections"}

    def get(self, request: HttpRequest, **kwargs: Dict[Any, Any]) -> HttpResponse:
        # maintain compatibility with .net urls: collection?id=1
        if request.GET.get("id"):
            return redirect("collection:item", pk=request.GET.get("id"))

        return super().get(request, **kwargs)


class CollectionDetails(LoginRequiredMixin, DetailView):
    template_name = "collection/one.html.dj"
    context_object_name = "collection"
    queryset = (
        Collections.objects.select_related("initiative", "modified_by")
        .prefetch_related("reports", "reports__report")
        .prefetch_related("reports__report__docs")
        .prefetch_related("reports__report__imgs")
        .prefetch_related("reports__report__type")
        .prefetch_related("reports__report__starred", "reports__report__starred__owner")
        .prefetch_related("reports__report__tags", "reports__report__tags__tag")
        .prefetch_related("terms", "terms__term", "terms__term__starred")
    )

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        context = super().get_context_data(**kwargs)

        context["title"] = self.object

        return context


class CollectionEdit(
    NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, UpdateView
):
    required_permissions = ("Edit Collection",)
    template_name = "collection/edit.html.dj"
    context_object_name = "collection"
    queryset = (
        Collections.objects.select_related("initiative")
        .prefetch_related("reports", "reports__report")
        .prefetch_related("terms", "terms__term")
    )
    fields: List[str] = []

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = f"Editing {self.object}"

        return context

    def post(
        self, request: HttpRequest, *args: Tuple[Any], **kwargs: Dict[Any, Any]
    ) -> HttpResponse:
        collection = Collections.objects.get(collection_id=self.kwargs["pk"])
        collection.name = request.POST.get("name", "")
        collection.search_summary = request.POST.get("search_summary", "")
        collection.description = request.POST.get("description", "")
        collection.hidden = request.POST.get("hidden", "N")
        collection.modified_by = request.user

        collection.save()

        # remove old links
        CollectionTerms.objects.filter(collection=collection).delete()
        CollectionReports.objects.filter(collection=collection).delete()

        # add new links
        for report_id in request.POST.getlist("linked_reports"):
            CollectionReports(collection=collection, report_id=report_id).save()

        for term_id in request.POST.getlist("linked_terms"):
            CollectionTerms(collection=collection, term_id=term_id).save()

        return redirect(collection.get_absolute_url() + "?success=Changes saved.")


class CollectionNew(LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    required_permissions = ("Create Collection",)
    template_name = "collection/new.html.dj"
    extra_context = {"title": "New Collection"}

    def post(self, request: HttpRequest) -> HttpResponse:
        collection = Collections(
            name=request.POST.get("name", ""),
            search_summary=request.POST.get("search_summary", ""),
            description=request.POST.get("description", ""),
            hidden=request.POST.get("hidden", "N"),
            modified_by=request.user,
        )

        collection.save()

        # add new links
        for report_id in request.POST.getlist("linked_reports"):
            CollectionReports(collection=collection, report_id=report_id).save()

        for term_id in request.POST.getlist("linked_terms"):
            CollectionTerms(collection=collection, term_id=term_id).save()

        return redirect(collection.get_absolute_url() + "?success=Changes saved.")  # type: ignore[no-untyped-call]


class CollectionDelete(LoginRequiredMixin, PermissionsCheckMixin, DeleteView):
    required_permissions = ("Delete Collection",)
    model = Collections
    template_name = "collection/new.html.dj"

    def get_success_url(self) -> str:
        return reverse("collection:list") + "?success=Collection successfully deleted."

    def get(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> HttpResponse:
        return redirect(
            resolve("collection:list")
            + "?error=You are not authorized to access that page."
        )

    def post(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> HttpResponse:
        pk = self.kwargs["pk"]

        CollectionTerms.objects.filter(collection_id=pk).delete()
        CollectionReports.objects.filter(collection_id=pk).delete()

        return super().post(*args, **kwargs)
