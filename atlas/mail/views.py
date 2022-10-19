from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse


# Create your views here.
@login_required
def index(request: HttpRequest) -> HttpResponse:

    return HttpResponse("<div></div>")


@login_required
def check(request: HttpRequest) -> HttpResponse:

    return HttpResponse("<div></div>")


@login_required
def mailbox(request: HttpRequest) -> HttpResponse:
    return HttpResponse("<div></div>")
