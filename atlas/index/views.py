"""Atlas home page."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(request):
    context = {
        "title": "Home",
    }

    return render(request, "index/index.html.dj", context)


@login_required
def about(request):
    context = {
        "title": "About",
    }

    return render(request, "index/about.html.dj", context)
