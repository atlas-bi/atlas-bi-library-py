import os
from email.mime.image import MIMEImage
from typing import Optional

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.http import HttpRequest
from django.template.loader import render_to_string
from htmlmin.minify import html_minify


def notification(
    request: HttpRequest,
    subject: str,
    recipient: models.Model,
    sender: models.Model,
    message: str,
    url: Optional[str] = None,
) -> None:
    context = {
        "subject": subject,
        "recipient": recipient,
        "sender": request.user,
        "message": message,
        "url": url,
    }

    msg_html = html_minify(
        render_to_string("mail/email.html.dj", context, request=request)
    )
    msg_text = render_to_string("mail/email_text.html.dj", context, request=request)

    reply_to = (
        [f"{sender} <{sender.email}>"]
        if sender.email
        else [settings.EMAIL_DEFAULT_REPLY_ADDRESS]
    )

    msg = EmailMultiAlternatives(
        subject,
        msg_text,
        from_email=f"{settings.EMAIL_SENDER_NAME} <{settings.EMAIL_SENDER_EMAIL}>",
        reply_to=reply_to,
        to=[recipient.email],
    )

    msg.mixed_subtype = "related"
    msg.attach_alternative(msg_html, "text/html")
    img_dir = "static"
    image = "img/atlas-logo.png"
    file_path = os.path.join(img_dir, image)
    with open(file_path, "rb") as f:
        img = MIMEImage(f.read())
        img.add_header("Content-ID", "<atlas_logo>")
        img.add_header("Content-Disposition", "inline", filename="atlas_logo")
    msg.attach(img)

    msg.send()
