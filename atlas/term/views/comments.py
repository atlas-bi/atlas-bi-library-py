"""Atlas Term Comments."""
# pylint: disable=C0116,C0115,W0613
import contextlib
import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import ListView
from index.models import TermComments, TermCommentStream, Terms

decorators = [never_cache, login_required]


@login_required
def comments_delete(request, pk, comment_id):
    data = json.loads(request.body.decode("UTF-8"))

    TermComments.objects.get(comment_id=comment_id).delete()

    if (
        data.get("stream")
        and TermCommentStream.objects.filter(stream_id=data.get("stream")).exists()
    ):
        TermComments.objects.filter(stream__stream_id=data.get("stream")).delete()
        TermCommentStream.objects.get(stream_id=data.get("stream")).delete()

    return redirect("term:comments", pk=pk)


@method_decorator(never_cache, name="get")
class Comments(LoginRequiredMixin, ListView):
    template_name = "comments.html.dj"
    context_object_name = "comments"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["comments_url"] = Terms.objects.get(
            term_id=self.kwargs["pk"]
        ).get_absolute_comments_url()

        return context

    def get_queryset(self):
        return (
            TermComments.objects.filter(stream__term_id=self.kwargs["pk"])
            .order_by("-stream_id", "comment_id")
            .all()
        )

    def post(self, request, pk):
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
                    comment_stream = TermCommentStream(term_id=pk)
                    comment_stream.save()

                comment = TermComments(
                    stream=comment_stream,
                    message=data.get("message"),
                    user=request.user,
                )
                comment.save()

        return super().get(request, pk=pk)
