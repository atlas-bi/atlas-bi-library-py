"""Atlas User views."""

import io
import json
import re

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
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
@never_cache
def index(request):
    """Get users stars."""
    reports = (
        request.user.starred_reports.select_related("report")
        .select_related("report__docs")
        .select_related("report__type")
        .filter(owner=request.user)
        .order_by("rank", "report__name")
    )

    # reports = (
    #     StarredReports.objects.select_related("report")
    #     .select_related("report__docs")
    #     .select_related("report__type")
    #     .filter(owner=request.user)
    #     .order_by("rank", "report__name")
    # )
    my_folders = FavoriteFolders.objects.filter(user=request.user)

    context = {
        "reports": reports,
        "my_folders": my_folders,
    }

    return render(request, "user/stars.html.dj", context)


@login_required
def create_folder(request):
    """Add a new folder for favorites."""
    data = json.loads(request.body.decode("UTF-8"))

    if request.method == "POST" and "folder_name" in data:

        folder = FavoriteFolders(name=data["folder_name"], user=request.user)
        folder.save()

        return JsonResponse({"folder_id": folder.folder_id}, status=200)

    return JsonResponse({"error": "failed to created folder."}, status=500)


def delete_folder(request):
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


def reorder_folder(request):
    """Change the order of a users favorites."""
    data = json.loads(request.body.decode("UTF-8"))

    if request.method == "POST":
        for folder in data:
            FavoriteFolders.objects.filter(user=request.user).filter(
                folder_id=folder["folder_id"]
            ).update(rank=folder["folder_rank"])

        return JsonResponse({"success": "reordered folders."}, status=200)
    return JsonResponse({"error": "failed to reorder folder."}, status=500)


def reorder(request):
    """Change the order of favorites."""
    # data = json.loads(request.body.decode("UTF-8"))

    if request.method == "POST":

        # for favorite in data:
        #     Favorites.objects.filter(user=request.user).filter(
        #         favorite_id=favorite["favorite_id"]
        #     ).update(rank=favorite["favorite_rank"])

        return JsonResponse({"success": "reordered favorites."}, status=200)
    return JsonResponse({"error": "failed to reorder favorites."}, status=500)


def change_folder(request):
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
