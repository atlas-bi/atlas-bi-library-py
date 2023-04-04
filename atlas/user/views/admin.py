"""Atlas User Admin views."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from index.models import UserPreferences, UserRoles

from atlas.decorators import admin_required


@admin_required
@login_required
def roles(request: HttpRequest) -> JsonResponse:
    """Get list of user roles."""
    return JsonResponse(list(UserRoles.objects.all().values()), safe=False)


@admin_required
@login_required
def disable_admin(request: HttpRequest) -> JsonResponse:
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
