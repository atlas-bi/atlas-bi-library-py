"""Atlas Project views."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from index.models import ProjectComments, Projects


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


@never_cache
@login_required
def comments(request, project_id):
    """Return term comments."""
    project_comments = (
        ProjectComments.objects.filter(stream_id__project_id=project_id)
        .order_by("-stream_id", "comment_id")
        .all()
    )
    context = {
        "permissions": request.user.get_permissions(),
        "comments": project_comments,
    }
    return render(
        request,
        "project_comments.html.dj",
        context,
    )
