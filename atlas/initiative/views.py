"""Atlas Initiative views."""
# pylint: disable=C0116,C0115,W0613,W0212

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView, View
from index.models import Collections, Initiatives


class InitiativeList(LoginRequiredMixin, ListView):
    queryset = Initiatives.objects.all().order_by("-_modified_at")
    context_object_name = "initiatives"
    template_name = "initiatives.html.dj"
    extra_context = {"title": "Initiatives"}

    def get(self, request, **kwargs):
        if request.GET.get("id"):
            return redirect("initiative:item", pk=request.GET.get("id"))

        return super().get(request, **kwargs)


class InitiativeDetails(LoginRequiredMixin, DetailView):
    template_name = "initiative.html.dj"
    context_object_name = "initiative"
    queryset = Initiatives.objects

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["favorite"] = (
            "favorite"
            if self.request.user.has_favorite("initiative", self.kwargs["pk"])
            else ""
        )
        context["title"] = self.object.name

        return context

    def post(self, request, **kwargs):
        initiative = Initiatives.objects.get(initiative_id=self.kwargs["pk"])

        initiative.name = request.POST.get("name", "")
        initiative.description = request.POST.get("description", "")
        initiative.ops_owner_id = request.POST.get("ops_owner_id")
        initiative.exec_owner_id = request.POST.get("exec_owner_id")
        initiative.financial_impact_id = request.POST.get("financial_impact_id")
        initiative.strategic_importance_id = request.POST.get("strategic_importance_id")
        initiative.modified_by = request.user
        initiative.save()

        # remove old links
        Collections.objects.filter(initiative=initiative).update(initiative=None)

        # add new links
        Collections.objects.filter(
            collection_id__in=request.POST.getlist("linked_data_collections")
        ).update(initiative=initiative)

        return redirect(initiative.get_absolute_url())


class InitiativeNew(LoginRequiredMixin, View):
    def post(self, request):
        initiative = Initiatives(
            name=request.POST.get("name", ""),
            description=request.POST.get("description", ""),
            ops_owner_id=request.POST.get("ops_owner_id"),
            exec_owner_id=request.POST.get("exec_owner_id"),
            financial_impact_id=request.POST.get("financial_impact_id"),
            strategic_importance_id=request.POST.get("strategic_importance_id"),
            modified_by=request.user,
        )

        initiative.save()

        # add new links
        Collections.objects.filter(
            collection_id__in=request.POST.getlist("linked_data_collections")
        ).update(initiative=initiative)

        return redirect(initiative.get_absolute_url())

    def get(self, request):
        return redirect("initiative:list")


@login_required
def delete(request, pk):
    """Delete a initiative.

    1. Updated linked collections to None
    2. delete initiative
    """
    Collections.objects.filter(initiative__initiative_id=pk).update(initiative=None)

    get_object_or_404(Initiatives, initiative_id=pk).delete()

    return redirect("initiative:list")
