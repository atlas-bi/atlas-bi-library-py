from django.urls import path

from . import apps, views

app_name = apps.CollectionConfig.name

urlpatterns = [
    path("", views.CollectionList.as_view(), name="list"),
    path("<int:pk>", views.CollectionDetails.as_view(), name="item"),
    path("new", views.CollectionNew.as_view(), name="new"),
    path("<int:pk>/edit", views.CollectionEdit.as_view(), name="edit"),
    path("<int:pk>/delete", views.CollectionDelete.as_view(), name="delete"),
]
