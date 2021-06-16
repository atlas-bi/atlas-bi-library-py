"""Atlas ETL for Search."""
import pysolr
from django.conf import settings
from django.http import HttpResponse


def index(request):
    """Test solr connections."""
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)
    return HttpResponse(solr.search("covid"))
