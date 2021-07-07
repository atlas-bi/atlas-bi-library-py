from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # search results handlebars template
    path("template", views.template, name="template"),
    # search for users for dropdowns
    path("user_lookup", views.user_lookup, name="user_lookup"),
    # search for users with role for dropdowns
    path("user_lookup/<str:role>", views.user_lookup, name="user_lookup"),
    # search for projects for dropdowns
    path("project_lookup", views.project_lookup, name="project_lookup"),
    # search for reports for dropdowns
    path("report_lookup", views.report_lookup, name="report_lookup"),
    # search for terms for dropdowns
    path("term_lookup", views.term_lookup, name="term_lookup"),
    # basic value lookups for dropdowns
    path("lookup/<str:lookup>", views.dropdown_lookup, name="dropdown_lookup"),
    # ajax search page. Type is typically "reports", "terms", "projects", etc.
    path("<str:search_type>/<str:search_string>", views.index, name="index"),
]
