from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(request):
    context = {
        "title": "Home",
    }

    return render(request, "index/index.html.dj", context)


@login_required
def video(request):
    video_status = request.user.get_preferences().filter(key="WelcomeToAtlasVideo")

    if video_status.exists():
        video_open = bool(video_status.first().value == 1)
    else:
        video_open = False

    context = {
        "video_open": video_open,
    }

    return render(request, "index/video.html.dj", context)
