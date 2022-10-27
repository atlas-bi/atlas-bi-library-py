import json
from typing import Any, Dict, Tuple

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.views.generic import View
from index.models import Groups, SharedItems, Users, UserSettings

from . import notification


# Create your views here.
@login_required
def index(request: HttpRequest) -> HttpResponse:

    return HttpResponse("<div></div>")


@login_required
def check(request: HttpRequest) -> HttpResponse:

    return HttpResponse("<div></div>")


@login_required
def mailbox(request: HttpRequest) -> HttpResponse:
    return HttpResponse("<div></div>")


@login_required
def send(request: HttpRequest) -> HttpResponse:
    return HttpResponse("<div></div>")


class Send(LoginRequiredMixin, View):
    def post(
        self, request: HttpRequest, *args: Tuple[Any], **kwargs: Dict[Any, Any]
    ) -> HttpResponse:

        data = json.loads(request.body)
        print(data)
        # print(request.POST)

        subject = data.get("subject")
        recipients = json.loads(data.get("recipient"))
        message = data.get("message")
        text = data.get("text")
        share = data.get("share")
        share_name = data.get("shareName")
        share_url = data.get("shareUrl")

        # get recipients
        recipient_users = Users.objects.filter(
            user_id__in=[int(x["userId"]) for x in recipients if x.get("type") == ""]
        )
        recipient_groups = Groups.objects.filter(
            group_id__in=[int(x["userId"]) for x in recipients if x.get("type") == "g"]
        )

        if not recipient_users and not recipient_groups:
            return HttpResponse("Error: No recipients specified!", content_type="text")

        # create a message
        for recipient in recipient_users:
            SharedItems.objects.create(
                sender=request.user, recipient=recipient, url=share_url, name=share_name
            )

            get_settings = UserSettings.objects.filter(
                user=recipient, name="share_notification"
            ).first()

            recipient_emails = get_settings.value if get_settings else "Y"

            print(recipient_emails)
            if recipient.email and recipient_emails:
                print("sending email")
                try:
                    notification(request, subject, recipient, request.user, message)
                    return HttpResponse("Message sent.")
                except BaseException as e:
                    print(e)
                    return HttpResponse("Failed to send message.")

            #     foreach (var group in GroupUserList)
            #     {
            #         SharedItem newShare =
            #             new()
            #             {
            #                 SharedFromUserId = sender.UserId,
            #                 SharedToUserId = group.UserId,
            #                 ShareDate = DateTime.Now,
            #                 Name = ShareName,
            #                 Url = ShareUrl
            #             };
            #         await _context.AddAsync(newShare);
            #         await _context.SaveChangesAsync();

            #         var GroupUserSetting = await _context.UserSettings
            #             .Where(x => x.Name == "share_notification" && x.UserId == group.UserId)
            #             .Select(x => x.Value)
            #             .FirstOrDefaultAsync();

            #         // iddea = use the group email address when possible. here the group is already expanded.
            #         if (!string.IsNullOrEmpty(group.User.Email) && GroupUserSetting != "N")
            #         {
            #             ViewData["Subject"] = $"New share from {sender.FullnameCalc}";
            #             ViewData["Body"] = Helpers.HtmlHelpers.MarkdownToHtml(Message, _config);
            #             ViewData["Sender"] = sender;
            #             ViewData["Receiver"] = group.User;

            #             var msgbody = await _renderer.RenderPartialToStringAsync(
            #                 "_EmailTemplate",
            #                 ViewData
            #             );
            #             await _emailer.SendAsync(
            #                 $"New share from {sender.FullnameCalc}",
            #                 HtmlHelpers.MinifyHtml(msgbody),
            #                 sender.Email,
            #                 group.User.Email
            #             );
            #         }
            #     }

        return HttpResponse("sent", content_type="text")
