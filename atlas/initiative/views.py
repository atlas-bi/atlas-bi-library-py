"""Atlas Initiative views."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from index.models import Initiatives


# Create your views here.
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
