from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # search results handlebars template
    path("template", views.template, name="template"),
    # search for users for dropdowns
    path("user_lookup", views.user_lookup, name="user_lookup"),
    # search for projects for dropdowns
    path("project_lookup", views.project_lookup, name="project_lookup"),
    # basic value lookups for dropdowns
    path("lookup/<str:lookup>", views.lookup, name="lookup"),
    # ajax search page. Type is typically "reports", "terms", "projects", etc.
    path("<str:search_type>/<str:search_string>", views.index, name="index"),
]
