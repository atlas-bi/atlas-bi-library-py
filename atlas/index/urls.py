from django.urls import path
from django.views.generic.base import RedirectView

from . import apps, views

app_name = apps.IndexConfig.name

favicon_view = RedirectView.as_view(url="/static/img/favicon.ico", permanent=True)
apple_touch_icon_precomposed = RedirectView.as_view(
    url="/static/img/apple-touch-icon-precomposed.png", permanent=True
)
apple_touch_icon = RedirectView.as_view(
    url="/static/img/apple-touch-icon.png", permanent=True
)

urlpatterns = [
    path("", views.index, name="index"),
    path("about_analytics", views.about, name="about"),
    path("favicon.ico", favicon_view),
    path("apple-touch-icon-precomposed.png", apple_touch_icon_precomposed),
    path("apple-touch-icon.png", apple_touch_icon),
]
