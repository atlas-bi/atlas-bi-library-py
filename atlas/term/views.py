"""Atlas Term views."""

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from index.models import Reports, TermComments, Terms


# Create your views here.
@login_required
def index(request):
    """Return main term list."""
    # maintain compatibility with dotnet urls.
    if request.GET.get("id"):
        return redirect("/terms/%s" % request.GET.get("id"))

    context = {
        "permissions": request.user.get_permissions(),
        "user": request.user,
        "favorites": request.user.get_favorites(),
        "terms": Terms.objects.all().order_by("-approved", "-_modified_at"),
        "title": "Terms",
    }

    return render(
        request,
        "terms.html.dj",
        context,
    )


@login_required
def item(request, term_id):
    """Return specific term."""
    try:
        term = Terms.objects.get(term_id=term_id)
    except Terms.DoesNotExist:
        return redirect(index)

    related_reports = (
        Reports.objects.filter(
            # linked terms
            Q(report_docs__report_terms__term_id=term_id)
            |
            # parent linked terms
            Q(parent__child__report_docs__report_terms__term_id=term_id)
            |
            # grandparent linked terms
            Q(parent__child__parent__child__report_docs__report_terms__term_id=term_id)
            |
            # great grandparent linked terms
            # pylint: disable=C0301
            Q(
                parent__child__parent__child__parent__child__report_docs__report_terms__term_id=term_id  # noqa: E501
            )
        )
        .filter(Q(report_docs__hidden="N") | Q(report_docs__hidden__isnull=True))
        .filter(visible="Y")
    ).distinct()

    context = {
        "permissions": request.user.get_permissions(),
        "user": request.user,
        "favorites": request.user.get_favorites(),
        "term": term,
        "title": term.name,
        "favorite": "favorite" if request.user.has_favorite("term", term_id) else "",
        "related_reports": related_reports,
    }

    return render(
        request,
        "term.html.dj",
        context,
    )


@never_cache
@login_required
def comments(request, term_id):
    """Return term comments."""
    term_comments = (
        TermComments.objects.filter(stream_id__term_id=term_id)
        .order_by("-stream_id", "comment_id")
        .all()
    )
    context = {
        "permissions": request.user.get_permissions(),
        "comments": term_comments,
    }
    return render(
        request,
        "term_comments.html.dj",
        context,
    )
