"""Atlas User views."""

import io
import json
import re

from django.contrib.auth.decorators import login_required
from django.db.models import Count, F
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
def index(request, pk=None):
    """Get users stars."""

    if pk:
        user = get_object_or_404(Users, pk=pk)
    else:
        user = request.user
    reports = (
        user.starred_reports.select_related("report")
        .select_related("report__docs")
        .select_related("report__type")
        .prefetch_related("report__attachments")
        .prefetch_related("report__tag_links__tag")
        .prefetch_related("report__starred")
        .order_by("rank", "report__name")
    )

    collections = (
        user.starred_collections.select_related("collection")
        .prefetch_related("collection__starred")
        .order_by("rank", "collection__name")
    )

    initiatives = (
        user.starred_initiatives.select_related("initiative")
        .prefetch_related("initiative__starred")
        .order_by("rank", "initiative__name")
    )

    terms = (
        user.starred_terms.select_related("term")
        .prefetch_related("term__starred")
        .order_by("rank", "term__name")
    )

    groups = (
        user.starred_groups.select_related("group")
        .prefetch_related("group__starred")
        .order_by("rank", "group__group_name")
    )

    users = (
        user.starred_users.select_related("user")
        .prefetch_related("user__starred")
        .order_by("rank", "user__full_name")
    )

    folders = FavoriteFolders.objects.filter(user=user).order_by(
        F("rank").asc(nulls_last=True), "name"
    )

    context = {
        "reports": reports,
        "collections": collections,
        "initiatives": initiatives,
        "terms": terms,
        "groups": groups,
        "users": users,
        "total": reports.count()
        + collections.count()
        + initiatives.count()
        + terms.count()
        + groups.count()
        + users.count(),
        "is_me": (pk is None or pk == request.user.user_id),
        "folders": folders,
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
