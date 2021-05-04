from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
@login_required
def index(request):

    return HttpResponse("Hello")


@login_required
def check(request):

    return HttpResponse("Hello")
