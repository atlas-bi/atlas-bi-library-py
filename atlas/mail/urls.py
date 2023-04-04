from django.urls import path

from . import apps, views

app_name = apps.MailConfig.name

urlpatterns = [
    path("share", views.Share.as_view(), name="share"),
    path("remove_share/<int:pk>", views.RemoveShare.as_view(), name="remove_share"),
]
