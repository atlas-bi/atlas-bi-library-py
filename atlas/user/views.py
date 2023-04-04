"""Atlas User views."""

import io
import json
import re

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache
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
def change_role(request):
    """Change user role."""
    role_id = request.GET.get("id", "")
    redirect_url = request.GET.get("url", "/")
    return JsonResponse({"role": role_id, "url": redirect_url}, status=200)


@login_required
def preference_video(request, state):
    """Set video preference."""
    video_status = request.user.get_preferences().filter(key="WelcomeToAtlasVideo")
    if video_status.exists():
        video_open = video_status.first()
        video_open.value = state
        video_open.save()
    else:
        UserPreferences.objects.create(
            key="WelcomeToAtlasVideo", user_id=request.user, value=state
        )
        video_open = False

    return JsonResponse({}, status=200)


@login_required
@never_cache
def favorites(request):
    """Get users favorites."""
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

    return render(request, "user/favorites.html.dj", context)


@login_required
def favorites_create_folder(request):
    """Add a new folder for favorites."""
    data = json.loads(request.body.decode("UTF-8"))

    if request.method == "POST" and "folder_name" in data:
        folder = FavoriteFolders(name=data["folder_name"], user=request.user)
        folder.save()

        return JsonResponse({"folder_id": folder.folder_id}, status=200)

    return JsonResponse({"error": "failed to created folder."}, status=500)


def favorites_delete_folder(request):
    """Delete a favorites folder."""
    data = json.loads(request.body.decode("UTF-8"))

    if request.method == "POST" and "folder_id" in data:
        # remove any report links to this folder
        # Favorites.objects.filter(folder__folder_id=data["folder_id"]).update(
        #     folder=None
        # )

        # remove the folder
        FavoriteFolders.objects.get(folder_id=data["folder_id"]).delete()

        return JsonResponse({"folder_id": data["folder_id"]}, status=200)
    return JsonResponse({"error": "failed to delete folder."}, status=500)


def favorites_reorder_folder(request):
    """Change the order of a users favorites."""
    data = json.loads(request.body.decode("UTF-8"))

    if request.method == "POST":
        for folder in data:
            FavoriteFolders.objects.filter(user=request.user).filter(
                folder_id=folder["folder_id"]
            ).update(rank=folder["folder_rank"])

        return JsonResponse({"success": "reordered folders."}, status=200)
    return JsonResponse({"error": "failed to reorder folder."}, status=500)


def favorites_reorder(request):
    """Change the order of favorites."""
    # data = json.loads(request.body.decode("UTF-8"))

    if request.method == "POST":
        # for favorite in data:
        #     Favorites.objects.filter(user=request.user).filter(
        #         favorite_id=favorite["favorite_id"]
        #     ).update(rank=favorite["favorite_rank"])

        return JsonResponse({"success": "reordered favorites."}, status=200)
    return JsonResponse({"error": "failed to reorder favorites."}, status=500)


def image(request, pk):
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


def favorites_change_folder(request):
    """Move a favorite between folders."""
    # data = json.loads(request.body.decode("UTF-8"))

    # Favorites.objects.filter(user=request.user).filter(
    #     favorite_id=data["favorite_id"]
    # ).update(folder=data["folder_id"])

    # return current folders and count

    folder_counts = list(
        FavoriteFolders.objects.filter(user=request.user)
        .values("folder_id")
        .annotate(count=Count("favorites"))
    )

    folder_counts.append(
        {
            "folder_id": "all",
            # "count": Favorites.objects.filter(user=request.user).count(),
        }
    )
    return JsonResponse(folder_counts, safe=False, status=200)
