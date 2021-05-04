from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:initiative_id>", views.item, name="item"),
    # path("<int:initiative_id>/comments", views.comments, name="comments"),
]
