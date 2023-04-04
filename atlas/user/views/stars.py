"""Atlas User views."""

import json
from typing import Optional

from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache
from index.models import (
    FavoriteFolders,
    StarredCollections,
    StarredGroups,
    StarredInitiatives,
    StarredReports,
    StarredSearches,
    StarredTerms,
    StarredUsers,
    Users,
)


@login_required
@never_cache
def index(request: HttpRequest, pk: Optional[int] = None) -> HttpResponse:
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
        .prefetch_related("report__tags__tag")
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
        .order_by("rank", "group__name")
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
@never_cache
def edit(request: HttpRequest) -> JsonResponse:
    """Add or remove a star."""
    star_id = request.GET.get("id", None)

    star_type = request.GET.get("type", "report")

    if star_type == "report":
        if (
            StarredReports.objects.filter(owner=request.user)
            .filter(report_id=star_id)
            .exists()
        ):
            StarredReports.objects.filter(owner=request.user).filter(
                report_id=star_id
            ).delete()
        else:
            report = StarredReports(owner=request.user, report_id=star_id)
            report.save()

        return JsonResponse(
            {"count": StarredReports.objects.filter(report_id=star_id).count()}
        )

    elif star_type == "collection":
        if (
            StarredCollections.objects.filter(owner=request.user)
            .filter(collection_id=star_id)
            .exists()
        ):
            StarredCollections.objects.filter(owner=request.user).filter(
                collection_id=star_id
            ).delete()
        else:
            collection = StarredCollections(owner=request.user, collection_id=star_id)
            collection.save()

        return JsonResponse(
            {"count": StarredCollections.objects.filter(collection_id=star_id).count()}
        )

    elif star_type == "initiative":
        if (
            StarredInitiatives.objects.filter(owner=request.user)
            .filter(initiative_id=star_id)
            .exists()
        ):
            StarredInitiatives.objects.filter(owner=request.user).filter(
                initiative_id=star_id
            ).delete()
        else:
            initiative = StarredInitiatives(owner=request.user, initiative_id=star_id)
            initiative.save()

        return JsonResponse(
            {"count": StarredInitiatives.objects.filter(initiative_id=star_id).count()}
        )

    elif star_type == "term":
        if (
            StarredTerms.objects.filter(owner=request.user)
            .filter(term_id=star_id)
            .exists()
        ):
            StarredTerms.objects.filter(owner=request.user).filter(
                term_id=star_id
            ).delete()
        else:
            term = StarredTerms(owner=request.user, term_id=star_id)
            term.save()

        return JsonResponse(
            {"count": StarredTerms.objects.filter(term_id=star_id).count()}
        )

    elif star_type == "user":
        if (
            StarredUsers.objects.filter(owner=request.user)
            .filter(user_id=star_id)
            .exists()
        ):
            StarredUsers.objects.filter(owner=request.user).filter(
                user_id=star_id
            ).delete()
        else:
            user = StarredUsers(owner=request.user, user_id=star_id)
            user.save()

        return JsonResponse(
            {"count": StarredUsers.objects.filter(user_id=star_id).count()}
        )

    elif star_type == "group":
        if (
            StarredGroups.objects.filter(owner=request.user)
            .filter(group_id=star_id)
            .exists()
        ):
            StarredGroups.objects.filter(owner=request.user).filter(
                group_id=star_id
            ).delete()
        else:
            group = StarredGroups(owner=request.user, group_id=star_id)
            group.save()

        return JsonResponse(
            {"count": StarredGroups.objects.filter(group_id=star_id).count()}
        )

    elif star_type == "search":
        if (
            StarredSearches.objects.filter(owner=request.user)
            .filter(search_id=star_id)
            .exists()
        ):
            StarredSearches.objects.filter(owner=request.user).filter(
                search_id=star_id
            ).delete()
        else:
            search = StarredSearches(owner=request.user, search_id=star_id)
            search.save()

    return JsonResponse({"success": "edited star."}, status=200)


@login_required
def create_folder(request: HttpRequest) -> JsonResponse:
    """Add a new folder for favorites."""
    name = request.GET.get("name", None)

    if name:
        folder = FavoriteFolders(name=name, user=request.user)
        folder.save()

        return JsonResponse({"folder_id": folder.folder_id}, status=200)

    return JsonResponse({"error": "failed to created folder."}, status=500)


@login_required
def edit_folder(request: HttpRequest, pk: int) -> JsonResponse:
    """Add a new folder for favorites."""
    name = request.GET.get("name", None)
    folder = get_object_or_404(FavoriteFolders, pk=pk, user=request.user)
    if name:
        folder.name = name
        folder.save()

        return JsonResponse({"folder_id": folder.folder_id}, status=200)

    return JsonResponse({"error": "failed to created folder."}, status=500)


@login_required
def delete_folder(request: HttpRequest, pk: int) -> JsonResponse:
    """Delete a favorites folder."""
    if request.method == "POST":
        folder = FavoriteFolders.objects.get(folder_id=pk)

        folder.starred_reports.update(folder=None)
        folder.starred_initiatives.update(folder=None)
        folder.starred_collections.update(folder=None)
        folder.starred_terms.update(folder=None)
        folder.starred_users.update(folder=None)
        folder.starred_groups.update(folder=None)

        folder.delete()

        return JsonResponse({"folder_id": pk}, status=200)
    return JsonResponse({"error": "failed to delete folder."}, status=500)


@login_required
def reorder_folder(request: HttpRequest) -> JsonResponse:
    """Change the order of a users favorites."""
    data = json.loads(request.body.decode("UTF-8"))

    if request.method == "POST":
        for folder in data:
            FavoriteFolders.objects.filter(user=request.user).filter(
                folder_id=folder["folder_id"]
            ).update(rank=folder["rank"])

        return JsonResponse({"success": "reordered folders."}, status=200)
    return JsonResponse({"error": "failed to reorder folder."}, status=500)


@login_required
def reorder(request: HttpRequest) -> JsonResponse:
    """Change the order of favorites."""
    data = json.loads(request.body.decode("UTF-8"))

    if request.method == "POST":
        for favorite in data:
            if favorite["type"] == "report":
                StarredReports.objects.filter(owner=request.user).filter(
                    star_id=favorite["star_id"]
                ).update(rank=favorite["rank"])
            elif favorite["type"] == "collection":
                StarredCollections.objects.filter(owner=request.user).filter(
                    star_id=favorite["star_id"]
                ).update(rank=favorite["rank"])
            elif favorite["type"] == "initiative":
                StarredInitiatives.objects.filter(owner=request.user).filter(
                    star_id=favorite["star_id"]
                ).update(rank=favorite["rank"])
            elif favorite["type"] == "term":
                StarredTerms.objects.filter(owner=request.user).filter(
                    star_id=favorite["star_id"]
                ).update(rank=favorite["rank"])
            elif favorite["type"] == "user":
                StarredUsers.objects.filter(owner=request.user).filter(
                    star_id=favorite["star_id"]
                ).update(rank=favorite["rank"])
            elif favorite["type"] == "group":
                StarredGroups.objects.filter(owner=request.user).filter(
                    star_id=favorite["star_id"]
                ).update(rank=favorite["rank"])
            elif favorite["type"] == "search":
                StarredSearches.objects.filter(owner=request.user).filter(
                    star_id=favorite["star_id"]
                ).update(rank=favorite["rank"])

        return JsonResponse({"success": "reordered favorites."}, status=200)
    return JsonResponse({"error": "failed to reorder favorites."}, status=500)


@login_required
def change_folder(request: HttpRequest) -> JsonResponse:
    """Move a favorite between folders."""
    data = json.loads(request.body.decode("UTF-8"))

    if request.method == "POST":
        if data["type"] == "report":
            StarredReports.objects.filter(owner=request.user).filter(
                star_id=data["star_id"]
            ).update(folder_id=data["folder_id"])
        elif data["type"] == "collection":
            StarredCollections.objects.filter(owner=request.user).filter(
                star_id=data["star_id"]
            ).update(folder_id=data["folder_id"])
        elif data["type"] == "initiative":
            StarredInitiatives.objects.filter(owner=request.user).filter(
                star_id=data["star_id"]
            ).update(folder_id=data["folder_id"])
        elif data["type"] == "term":
            StarredTerms.objects.filter(owner=request.user).filter(
                star_id=data["star_id"]
            ).update(folder_id=data["folder_id"])
        elif data["type"] == "user":
            StarredUsers.objects.filter(owner=request.user).filter(
                star_id=data["star_id"]
            ).update(folder_id=data["folder_id"])
        elif data["type"] == "group":
            StarredGroups.objects.filter(owner=request.user).filter(
                star_id=data["star_id"]
            ).update(folder_id=data["folder_id"])
        elif data["type"] == "search":
            StarredSearches.objects.filter(owner=request.user).filter(
                star_id=data["star_id"]
            ).update(folder_id=data["folder_id"])

        return JsonResponse({"success": "moved star to folder."}, status=200)
    return JsonResponse({"error": "failed to move star to folder."}, status=500)
