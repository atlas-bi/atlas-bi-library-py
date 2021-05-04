from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from index.models import UserPreferences, UserRoles

# Create your views here.


@login_required
def roles(request):
    return JsonResponse(list(UserRoles.objects.all().values()), safe=False)


@login_required
def change_role(request):
    role_id = request.GET.get("id", "")
    redirect_url = request.GET.get("url", "/")
    return JsonResponse({}, status=200)


@login_required
def preference_video(request, state):

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
