# pylint: disable=C0103,C0114

from django.urls import path

from . import apps, views

app_name = apps.TermConfig.name

urlpatterns = [
    path("", views.TermList.as_view(), name="list"),
    path("<int:pk>", views.TermDetails.as_view(), name="item"),
    path("new", views.TermNew.as_view(), name="new"),
    path("<int:pk>/edit", views.TermEdit.as_view(), name="edit"),
    path("<int:pk>/delete", views.TermDelete.as_view(), name="delete"),
]
