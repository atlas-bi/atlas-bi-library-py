"""Atlas home page."""
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """Home page."""
    context = {
        "title": "Home",
    }

    return render(request, "index/index.html.dj", context)


@login_required
def about(request: HttpRequest) -> HttpResponse:
    """About analytics page."""
    context = {
        "title": "About",
    }

    return render(request, "index/about.html.dj", context)
