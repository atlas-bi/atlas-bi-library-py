# pylint: disable=C0103,C0114
from django.urls import path

from . import apps, views

app_name = apps.InitiativeConfig.name

urlpatterns = [
    path("", views.InitiativeList.as_view(), name="list"),
    path("<int:pk>", views.InitiativeDetails.as_view(), name="item"),
    path("new", views.InitiativeNew.as_view(), name="new"),
    path("<int:pk>/edit", views.InitiativeEdit.as_view(), name="edit"),
    path("<int:pk>/delete", views.InitiativeDelete.as_view(), name="delete"),
]
