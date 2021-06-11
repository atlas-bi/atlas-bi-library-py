import pysolr
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render


def index(request):

    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)
    return HttpResponse(solr.search("covid"))
