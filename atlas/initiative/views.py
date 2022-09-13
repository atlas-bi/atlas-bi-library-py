"""Atlas Initiative views."""
# pylint: disable=C0116,C0115,W0613,W0212,R0201

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
from index.models import Collections, Initiatives

from atlas.decorators import NeverCacheMixin, PermissionsCheckMixin


class InitiativeList(LoginRequiredMixin, ListView):
    queryset = Initiatives.objects.all().order_by("-_modified_at")
    context_object_name = "initiatives"
    template_name = "initiative/all.html.dj"
    extra_context = {"title": "Initiatives"}

    def get(self, request, **kwargs):
        if request.GET.get("id"):
            return redirect("initiative:item", pk=request.GET.get("id"))

        return super().get(request, **kwargs)


class InitiativeDetails(LoginRequiredMixin, DetailView):
    template_name = "initiative/one.html.dj"
    context_object_name = "initiative"
    queryset = Initiatives.objects

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["title"] = self.object

        return context


class InitiativeEdit(
    NeverCacheMixin, LoginRequiredMixin, PermissionsCheckMixin, UpdateView
):
    required_permissions = ("Edit Initiative",)
    template_name = "initiative/edit.html.dj"
    context_object_name = "initiative"
    queryset = Initiatives.objects
    fields = ["description"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Editing {self.object}"

        return context

    def post(self, request, *args, **kwargs):
        initiative = Initiatives.objects.get(initiative_id=self.kwargs["pk"])

        initiative.name = request.POST.get("name", "")
        initiative.description = request.POST.get("description", "")
        initiative.ops_owner_id = request.POST.get("ops_owner_id")
        initiative.exec_owner_id = request.POST.get("exec_owner_id")
        initiative.financial_impact_id = request.POST.get("financial_impact_id")
        initiative.strategic_importance_id = request.POST.get("strategic_importance_id")
        initiative.modified_by = request.user
        initiative.hidden = request.POST.get("hidden", "N")
        initiative.save()

        # remove old links
        Collections.objects.filter(initiative=initiative).update(initiative=None)

        # add new links
        Collections.objects.filter(
            collection_id__in=request.POST.getlist("linked_data_collections")
        ).update(initiative=initiative)

        return redirect(initiative.get_absolute_url())


class InitiativeNew(LoginRequiredMixin, PermissionsCheckMixin, TemplateView):
    required_permissions = ("Create Initiative",)
    template_name = "initiative/new.html.dj"
    extra_context = {"title": "New Initiative"}

    def post(self, request, *args, **kwargs):
        initiative = Initiatives(
            name=request.POST.get("name", ""),
            description=request.POST.get("description", ""),
            ops_owner_id=request.POST.get("ops_owner_id"),
            exec_owner_id=request.POST.get("exec_owner_id"),
            financial_impact_id=request.POST.get("financial_impact_id"),
            strategic_importance_id=request.POST.get("strategic_importance_id"),
            hidden=request.POST.get("hidden", "N"),
            modified_by=request.user,
        )

        initiative.save()

        # add new links
        Collections.objects.filter(
            collection_id__in=request.POST.getlist("linked_data_collections")
        ).update(initiative=initiative)

        return redirect(initiative.get_absolute_url())


class InitiativeDelete(LoginRequiredMixin, PermissionsCheckMixin, DeleteView):
    required_permissions = ("Delete Initiative",)
    model = Initiatives
    success_url = reverse_lazy("initiative:list")

    def get(self, *args, **kwargs):
        return redirect("initiative:list")

    def post(self, *args, **kwargs):
        """Delete a initiative.

        1. Updated linked collections to None
        2. delete
        """
        pk = self.kwargs["pk"]

        Collections.objects.filter(initiative__initiative_id=pk).update(initiative=None)

        return super().post(*args, **kwargs)
