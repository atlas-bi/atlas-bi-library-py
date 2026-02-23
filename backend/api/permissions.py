from __future__ import annotations

from collections.abc import Iterable

from atlas_index.models import (
    AtlasUser,
    GroupRoleLinks,
    RolePermissions,
    UserGroupMemberships,
    UserPreferences,
    UserRoleLinks,
    UserRoles,
)
from rest_framework.permissions import BasePermission


def get_atlas_user_for_request_user(request_user) -> AtlasUser | None:
    email = (getattr(request_user, "email", None) or "").strip()
    username = (getattr(request_user, "username", None) or "").strip()

    if email:
        obj = AtlasUser.objects.filter(email__iexact=email).first()
        if obj is not None:
            return obj

    if username:
        obj = AtlasUser.objects.filter(username__iexact=username).first()
        if obj is not None:
            return obj

    return None


def _atlas_user_has_active_admin(atlas_user: AtlasUser) -> bool:
    admin_disabled = UserPreferences.objects.filter(
        user=atlas_user, key="AdminDisabled"
    ).exists()
    if admin_disabled:
        return False

    if UserRoleLinks.objects.filter(
        user=atlas_user, role__name="Administrator"
    ).exists():
        return True

    group_ids = UserGroupMemberships.objects.filter(user=atlas_user).values_list(
        "group_id", flat=True
    )
    if GroupRoleLinks.objects.filter(
        group_id__in=group_ids, role__name="Administrator"
    ).exists():
        return True

    return False


def _atlas_user_permission_names(atlas_user: AtlasUser) -> set[str]:
    # If active admin, grant all permissions.
    if _atlas_user_has_active_admin(atlas_user):
        return set(RolePermissions.objects.all().values_list("name", flat=True))

    # Base permissions from the default "User" role.
    base_user_perms = set(
        RolePermissions.objects.filter(
            role_permission_links__role__name="User"
        ).values_list("name", flat=True)
    )

    # Direct user roles (excluding Administrator/User which are handled elsewhere).
    direct_perms = set(
        UserRoleLinks.objects.filter(user=atlas_user)
        .exclude(role__name__in=["Administrator", "User"])
        .values_list("role__permission_links__permission__name", flat=True)
    )

    # Group roles (excluding Administrator/User which are handled elsewhere).
    group_role_names = (
        UserRoles.objects.filter(
            name__in=UserGroupMemberships.objects.filter(user=atlas_user).values_list(
                "group__role_links__role__name", flat=True
            )
        )
        .exclude(name__in=["Administrator", "User"])
        .values_list("name", flat=True)
    )

    group_perms = set(
        UserRoles.objects.filter(name__in=group_role_names).values_list(
            "permission_links__permission__name", flat=True
        )
    )

    return base_user_perms | direct_perms | group_perms


class AtlasRolePermission(BasePermission):
    """Check Atlas SQLServer role permissions by permission *name*.

    Mirrors legacy library-py behavior where views specify required permission names
    like "Edit Collection".
    """

    required_permissions: tuple[str, ...] = ()

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        required: Iterable[str] = (
            getattr(view, "required_permissions", None) or self.required_permissions
        )
        required = tuple(required)
        if not required:
            return True

        atlas_user = get_atlas_user_for_request_user(request.user)
        if atlas_user is None:
            return False

        perms = _atlas_user_permission_names(atlas_user)
        return set(required).issubset(perms)
