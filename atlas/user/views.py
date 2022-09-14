"""Atlas User views."""

import io
import re

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from index.models import (
    FavoriteFolders,
    StarredReports,
    UserPreferences,
    UserRoles,
    Users,
)
from PIL import Image, ImageDraw, ImageFont

from atlas.decorators import admin_required


@login_required
def index(request, pk=None):
    """User profile page."""
    if pk:
        return render(
            request,
            "user/index.html.dj",
            {
                "user": get_object_or_404(Users, pk=pk),
                "is_me": (pk == request.user.user_id),
            },
        )
    return render(request, "user/index.html.dj")


@admin_required
@login_required
def roles(request):
    """Get list of user roles."""
    return JsonResponse(list(UserRoles.objects.all().values()), safe=False)


@admin_required
@login_required
def disable_admin(request):
    """Change user role."""
    next_url = request.GET.get("url", "/")

    if not url_has_allowed_host_and_scheme(next_url, request.get_host()):
        next_url = "/"

    if UserPreferences.objects.filter(key="AdminDisabled", user=request.user).exists():
        UserPreferences.objects.filter(key="AdminDisabled", user=request.user).delete()
    else:
        pref = UserPreferences(key="AdminDisabled", user=request.user)
        pref.save()

    return redirect(next_url)


@login_required
def subscriptions(request):
    """Get users subscriptions."""
    reports = (
        StarredReports.objects.select_related("report")
        .select_related("report__docs")
        .select_related("report__type")
        .filter(owner=request.user)
        .order_by("rank", "report__name")
    )
    my_folders = FavoriteFolders.objects.filter(user=request.user)

    context = {
        "reports": reports,
        "my_folders": my_folders,
    }

    return render(request, "user/subscriptions.html.dj", context)


@login_required
def groups(request):
    """Get users groups."""
    reports = (
        StarredReports.objects.select_related("report")
        .select_related("report__docs")
        .select_related("report__type")
        .filter(owner=request.user)
        .order_by("rank", "report__name")
    )
    my_folders = FavoriteFolders.objects.filter(user=request.user)

    context = {
        "reports": reports,
        "my_folders": my_folders,
    }

    return render(request, "user/groups.html.dj", context)


def image(request, pk):
    """Get user image."""
    user = get_object_or_404(Users, pk=pk)
    image_format = "webp"

    # Browsers (IE11) that do not support webp
    if "HTTP_USER_AGENT" in request.META:
        user_agent = request.META["HTTP_USER_AGENT"].lower()
        if "trident" in user_agent or "msie" in user_agent:
            image_format = "jpeg"

    size = request.GET.get("size", "")

    if re.match(r"^\d+x\d+$", size):
        width, height = (int(x) for x in size.split("x"))
        im = Image.new("RGB", (width, height), color=(197, 197, 197))
        fnt = ImageFont.truetype(
            "./static/font/rasa/files/rasa-latin-600-normal.ttf", 60
        )
        out = ImageDraw.Draw(im)
        out.text((15, 5), user.first_initial, font=fnt, fill=(149, 149, 149))

        buf = io.BytesIO()
        im.save(buf, format=image_format)

        response = HttpResponse(buf.getvalue(), content_type="application/octet-stream")
        response["Content-Disposition"] = 'attachment; filename="{}.{}"'.format(
            user.pk,
            image_format,
        )

        return response
    else:
        raise Http404("Image not found...")
