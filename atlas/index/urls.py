from django.urls import path
from django.views.generic.base import RedirectView

from . import views

favicon_view = RedirectView.as_view(url="/static/img/favicon.ico", permanent=True)

urlpatterns = [
    path("", views.index, name="index"),
    path("favicon.ico", favicon_view),
    path("welcome-video", views.video, name="video"),
]
