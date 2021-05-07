"""Atlas User views."""

from atlas.decorators import admin_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from index.models import UserPreferences, UserRoles


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
