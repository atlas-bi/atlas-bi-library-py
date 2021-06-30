"""Atlas Initiative views."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from index.models import Initiatives, Projects


@login_required
def index(request):
    """Return main initiative list."""
    # maintain compatibility with dotnet urls.
    if request.GET.get("id"):
        return redirect("/initiatives/%s" % request.GET.get("id"))

    context = {
        "permissions": request.user.get_permissions(),
        "user": request.user,
        "favorites": request.user.get_favorites(),
        "initiatives": Initiatives.objects.all().order_by("-_modified_at"),
        "title": "Initiatives",
    }

    return render(
        request,
        "initiatives.html.dj",
        context,
    )


@login_required
def item(request, initiative_id):
    """Return specific initiative."""
    try:
        initiative = Initiatives.objects.get(initiative_id=initiative_id)
    except Initiatives.DoesNotExist:
        return redirect(index)

    context = {
        "permissions": request.user.get_permissions(),
        "user": request.user,
        "favorites": request.user.get_favorites(),
        "initiative": initiative,
        "title": initiative.name,
        "favorite": "favorite"
        if request.user.has_favorite("initiative", initiative_id)
        else "",
    }

    return render(
        request,
        "initiative.html.dj",
        context,
    )


@login_required
def edit(request, initiative_id=None):
    """Save initiative edits."""
    if request.method == "GET":
        return redirect(index)

    initiative = (
        Initiatives.objects.get(initiative_id=initiative_id)
        if initiative_id
        else Initiatives()
    )
    initiative.name = request.POST.get("name", "")
    initiative.description = request.POST.get("description", "")
    initiative.ops_owner_id = request.POST.get("ops_owner_id")
    initiative.exec_owner_id = request.POST.get("exec_owner_id")
    initiative.financial_impact_id = request.POST.get("financial_impact")
    initiative.strategic_importance_id = request.POST.get("strategic_importance")
    initiative.modified_by = request.user
    initiative.save()

    Projects.objects.filter(
        project_id__in=request.POST.getlist("linked_data_projects")
    ).update(initiative=initiative)
    return redirect(item, initiative.initiative_id)


@login_required
def delete(request, initiative_id):
    """Delete a initiative.

    1. comments
    2. comment streams
    3. report doc initiative links
    4. project annotations
    5. initiative
    """
    Projects.objects.filter(initiative__initiative_id=initiative_id).update(
        initiative=None
    )
    Initiatives.objects.get(initiative_id=initiative_id).delete()

    return redirect(index)
