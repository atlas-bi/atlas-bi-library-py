from django.urls import path

from . import apps, views

app_name = apps.SketchConfig.name

urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("chart/<str:type>/<int:pk>", views.Chart.as_view(), name="chart"),
    path("users/<str:type>/<int:pk>", views.UserList.as_view(), name="users"),
    path("reports/<str:type>/<int:pk>", views.ReportList.as_view(), name="reports"),
    path("fails/<str:type>/<int:pk>", views.Fails.as_view(), name="fails"),
    path("stars/<str:type>/<int:pk>", views.Stars.as_view(), name="stars"),
    path("run_list/<str:type>/<int:pk>", views.RunList.as_view(), name="run_list"),
    path(
        "subscriptions/<str:type>/<int:pk>",
        views.Subscriptions.as_view(),
        name="subscriptions",
    ),
]
