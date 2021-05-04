from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render


@login_required
def index(request):

    context = {
        "permissions": request.user.get_permissions(),
        "user": request.user,
        "favorites": request.user.get_favorites(),
    }

    return render(request, "index.html.dj", context)


@login_required
def video(request):

    video_status = request.user.get_preferences().filter(key="WelcomeToAtlasVideo")

    if video_status.exists():
        video_open = bool(video_status.first().value == 1)
    else:
        video_open = False

    context = {
        "permissions": request.user.get_permissions(),
        "user": request.user,
        "favorites": request.user.get_favorites(),
        "video_open": video_open,
    }

    return render(request, "video.html.dj", context)
