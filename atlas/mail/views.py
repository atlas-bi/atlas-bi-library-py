import json
from typing import Any, Dict, Tuple

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.generic import View
from index.models import Groups, SharedItems, Users, UserSettings

from . import notification


class RemoveShare(LoginRequiredMixin, View):
    def post(
        self, request: HttpRequest, *args: Tuple[Any], **kwargs: Dict[Any, Any]
    ) -> HttpResponse:
        pk = self.kwargs["pk"]

        SharedItems.objects.filter(recipient_id=request.user.user_id, pk=pk).delete()

        return HttpResponse("Share removed.", content_type="text")


class Share(LoginRequiredMixin, View):
    def post(
        self, request: HttpRequest, *args: Tuple[Any], **kwargs: Dict[Any, Any]
    ) -> HttpResponse:
        data = json.loads(request.body)

        subject = data.get("subject")
        recipients = json.loads(data.get("recipient"))
        message = data.get("message")
        text = data.get("text")
        share = data.get("share")
        share_name = data.get("shareName")
        share_url = data.get("shareUrl")

        # get recipients
        recipient_users = (
            Users.objects.filter(
                group_links__group_id__in=[
                    int(x["userId"]) for x in recipients if x.get("type") == "g"
                ]
            )
            | Users.objects.filter(
                user_id__in=[
                    int(x["userId"]) for x in recipients if x.get("type") == ""
                ]
            )
        ).distinct()

        if not recipient_users:
            return HttpResponse("Error: No recipients specified!", content_type="text")

        # create a message
        for recipient in recipient_users:
            SharedItems.objects.create(
                sender=request.user,
                recipient=recipient,
                url=share_url,
                name=share_name,
                share_date=timezone.now(),
            )

            get_settings = UserSettings.objects.filter(
                user=recipient, name="share_notification"
            ).first()

            recipient_emails = get_settings.value if get_settings else "Y"

            if recipient.email and recipient_emails:
                try:
                    notification(
                        request,
                        f"New share from {request.user}",
                        recipient,
                        request.user,
                        message,
                        url=share_url,
                    )
                    return HttpResponse("Message sent.")
                except BaseException as e:
                    print(e)
                    return HttpResponse("Failed to send message.")

        return HttpResponse("sent", content_type="text")
