from django.urls import path

from . import apps, views

app_name = apps.MailConfig.name

urlpatterns = [
    path("", views.index, name="index"),
    path("check", views.check, name="check"),
    path("get_mailbox", views.mailbox, name="mailbox"),
    path("send", views.index, name="send"),
]
