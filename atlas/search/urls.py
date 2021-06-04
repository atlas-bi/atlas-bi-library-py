from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:search_string>", views.index, name="index"),
    path("search/<str:search_string>", views.search, name="search"),
    path("template", views.template, name="template"),
    path("lookup/<str:lookup>", views.lookup, name="lookup"),
]
