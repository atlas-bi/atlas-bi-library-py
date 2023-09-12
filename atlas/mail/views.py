from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


# Create your views here.
@login_required
def index(request):
    return HttpResponse("<div></div>")


@login_required
def check(request):
    return HttpResponse("<div></div>")


@login_required
def mailbox(request):
    return HttpResponse("<div></div>")
