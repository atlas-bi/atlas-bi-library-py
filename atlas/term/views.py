"""Atlas Term views."""
# pylint: disable=C0116,C0115,W0613,W0212, E1131

from typing import Any, Dict, List, Tuple

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, reverse
from django.urls import resolve
from django.utils import timezone
from django.views.generic import (
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
from index.models import CollectionTerms, Reports, ReportTerms, Terms

from atlas.decorators import NeverCacheMixin, PermissionsCheckMixin


class TermList(LoginRequiredMixin, ListView):
    queryset = Terms.objects.order_by("-approved", "-modified_at").prefetch_related(
        "starred"
    )
    context_object_name = "terms"
    template_name = "term/all.html.dj"
    extra_context = {"title": "Terms"}

    def get(self, request: HttpRequest, **kwargs: Dict[Any, Any]) -> HttpResponse:
        # maintain compatibility with .net urls: term?id=1
        if request.GET.get("id"):
            return redirect("term:item", pk=request.GET.get("id"))

        return super().get(request, **kwargs)


class TermDetails(LoginRequiredMixin, DetailView):
    template_name = "term/one.html.dj"
    context_object_name = "term"
    queryset = (
        Terms.objects.select_related("approved_by", "modified_by")
        .prefetch_related("collections__collection")
        .prefetch_related("starred")
    )

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        """Add additional items to the context."""
        context = super().get_context_data(**kwargs)

        term_id = self.kwargs["pk"]

        context["related_reports"] = (
            Reports.objects.filter(
                # link ed terms
                Q(docs__terms__term_id=term_id)
                |
                # parent linked terms
                Q(parent__child__docs__terms__term_id=term_id)
                |
                # grandparent linked terms
                Q(parent__child__parent__child__docs__terms__term_id=term_id)
                |
                # great grandparent linked terms
                # pylint: disable=C0301
                Q(
                    parent__child__parent__child__parent__child__docs__terms__term_id=term_id  # noqa: E501
                )
            )
            .filter(Q(docs__hidden="N") | Q(docs__hidden__isnull=True))
            .filter(visible="Y")
            .prefetch_related("imgs")
            .select_related("type")
            .prefetch_related("starred", "starred__owner")
            .prefetch_related("tags", "tags__tag")
            .prefetch_related("docs")
        ).distinct()

        context["title"] = self.object

        return context


class TermEdit(NeverCacheMixin, LoginRequiredMixin, UpdateView):
    template_name = "term/edit.html.dj"
    context_object_name = "term"
    fields: List[str] = []

    queryset = Terms.objects.select_related("approved_by").select_related("modified_by")

    def get_context_data(self, **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        """Add additional items to the context."""
        context = super().get_context_data(**kwargs)

        context["title"] = f"Editing {self.object}"

        return context

    def post(self, request: HttpRequest, **kwargs: Dict[Any, Any]) -> HttpResponse:
        term = Terms.objects.get(term_id=self.kwargs["pk"])

        if term.approved == "Y" and not request.user.has_perm("Edit Approved Terms"):
            return redirect(
                term.get_absolute_url()
                + "?error=You are not authorized to access that page."
            )

        if term.approved != "Y" and not request.user.has_perm("Edit Unapproved Terms"):
            return redirect(
                term.get_absolute_url()
                + "?error=You are not authorized to access that page."
            )

        term.name = request.POST.get("name", "")
        term.summary = request.POST.get("summary", "")
        term.technical_definition = request.POST.get("technical_definition", "")

        if (
            term.approved != "Y"
            and request.POST.get("approved", "N") == "Y"
            and request.user.has_perm("Approve Terms")
        ):
            # add date if term is now approved
            term._approved_at = timezone.now()
            term.approved = request.POST.get("approved", "N")

        elif term.approved == "Y" and request.POST.get("approved", "N") == "N":
            # remove date it term is now not approved
            term._approved_at = None
            term.approved = request.POST.get("approved", "N")

        term.external_standard_url = request.POST.get("external_standard_url", "")
        term._valid_from = request.POST.get("valid_from", "") or None
        term.modified_by = request.user

        term.save()

        return redirect("term:item", **kwargs)


class TermNew(LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    required_permissions = ("Create New Terms",)
    template_name = "term/new.html.dj"
    extra_context = {"title": "New Term"}

    def post(self, request: HttpRequest) -> HttpResponse:
        term = Terms(
            name=request.POST.get("name", ""),
            summary=request.POST.get("summary", ""),
            technical_definition=request.POST.get("technical_definition", ""),
            approved="N",
            external_standard_url=request.POST.get("external_standard_url", ""),
            _valid_from=(request.POST.get("valid_from", "") or None),
            modified_by=request.user,
        )

        if request.POST.get("approved", "N") == "Y" and request.user.has_perm(
            "Approve Terms"
        ):
            term._approved_at = timezone.now()
            term.approved = request.POST.get("approved", "N")

        term.save()

        return redirect("term:item", pk=term.term_id)


class TermDelete(LoginRequiredMixin, DeleteView):
    model = Terms
    template_name = "term/new.html.dj"

    def get_success_url(self) -> str:
        return reverse("term:list") + "?success=Term successfully deleted."

    def get(
        self, request: HttpRequest, *args: Tuple[Any], **kwargs: Dict[Any, Any]
    ) -> HttpResponse:
        return redirect(
            resolve("term:list") + "?error=You are not authorized to access that page."
        )

    def post(
        self, request: HttpRequest, *args: Tuple[Any], **kwargs: Dict[Any, Any]
    ) -> HttpResponse:
        pk = self.kwargs["pk"]

        term = self.get_object()
        if term.approved == "Y" and not request.user.has_perm("Delete Approved Terms"):
            return redirect(
                term.get_absolute_url()
                + "?error=You are not authorized to access that page."
            )

        if term.approved != "Y" and not request.user.has_perm(
            "Delete Unapproved Terms"
        ):
            return redirect(
                term.get_absolute_url()
                + "?error=You are not authorized to access that page."
            )

        ReportTerms.objects.filter(term__term_id=pk).delete()
        CollectionTerms.objects.filter(term__term_id=pk).delete()

        return super().post(request, *args, **kwargs)
