"""Atlas Term views."""

import contextlib
import json

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from index.models import (
    ProjectTerms,
    Reports,
    ReportTerms,
    TermComments,
    TermCommentStream,
    Terms,
)


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
        term = (
            Terms.objects.select_related("approved_by")
            .select_related("modified_by")
            .prefetch_related("report_docs")
            .prefetch_related("report_docs__report_doc")
            .prefetch_related("report_docs__report_doc__report")
            .prefetch_related("projects")
            .prefetch_related("projects__project")
            .prefetch_related("projects__project__initiative")
            .get(term_id=term_id)
        )
    except Terms.DoesNotExist:
        return redirect(index)

    related_reports = (
        Reports.objects.filter(
            # linked terms
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


@login_required
def comments_delete(request, term_id, comment_id):
    """Delete a comment or comment stream."""
    data = json.loads(request.body.decode("UTF-8"))

    TermComments.objects.get(comment_id=comment_id).delete()

    if (
        data.get("stream")
        and TermCommentStream.objects.filter(stream_id=data.get("stream")).exists()
    ):

        TermComments.objects.filter(stream__stream_id=data.get("stream")).delete()
        TermCommentStream.objects.get(stream_id=data.get("stream")).delete()

    return redirect(comments, term_id)


@never_cache
@login_required
def comments(request, term_id):
    """Return a terms comments."""
    if request.method == "GET":
        term_comments = (
            TermComments.objects.filter(stream__term_id=term_id)
            .order_by("-stream_id", "comment_id")
            .all()
        )
        context = {
            "permissions": request.user.get_permissions(),
            "comments": term_comments,
            "term_id": term_id,
        }
        return render(
            request,
            "term_comments.html.dj",
            context,
        )

    with contextlib.suppress("json.decoder.JSONDecodeError"):
        data = json.loads(request.body.decode("UTF-8"))

        if data.get("message", "") != "":

            if (
                data.get("stream")
                and TermCommentStream.objects.filter(
                    stream_id=data.get("stream")
                ).exists()
            ):
                comment_stream = TermCommentStream.objects.filter(
                    stream_id=data.get("stream")
                ).first()
            else:
                comment_stream = TermCommentStream(term_id=term_id)
                comment_stream.save()

            comment = TermComments(
                stream=comment_stream, message=data.get("message"), user=request.user
            )
            comment.save()

    return redirect(comments, term_id)


@login_required
def edit(request, term_id=None):
    """Save term edits."""
    if request.method == "GET":
        return redirect(index)

    term = Terms.objects.get(term_id=term_id) if term_id else Terms()
    term.name = request.POST.get("name", "")
    term.summary = request.POST.get("summary", "")
    term.technical_definition = request.POST.get("technical_definition", "")

    if term.approved != "Y" and request.POST.get("approved", "N") == "Y":
        # add date if term is now approved
        term._approved_at = timezone.now()
    elif term.approved == "Y" and request.POST.get("approved", "N") == "N":
        # remove date it term is now not approved
        term._approved_at = None

    term.approved = request.POST.get("approved", "N")
    term.external_standard_url = request.POST.get("external_standard_url", None)
    term.has_external_standard = (
        "Y" if bool(request.POST.get("external_standard_url", "")) else None
    )
    term._valid_from = request.POST.get("valid_from", None)
    term.modified_by = request.user

    term.save()

    return redirect(item, term.term_id)


@login_required
def delete(request, term_id):
    """Delete a term.

    1. comments
    2. comment streams
    3. report doc term links
    4. project annotations
    5. term
    """
    TermComments.objects.filter(stream_id__term_id=term_id).delete()
    TermCommentStream.objects.filter(term_id=term_id).delete()
    ReportTerms.objects.filter(term__term_id=term_id).delete()
    ProjectTerms.objects.filter(term__term_id=term_id).delete()
    Terms.objects.get(term_id=term_id).delete()

    return redirect(index)
