from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from index.models import ReportImages, Reports


# Create your views here.
@login_required
def index(request, report_id):

    permissions = [19, 12]

    report = Reports.objects.get(report_id=report_id)

    favorite = "yes" if request.user.has_favorite("report", report_id) else "no"

    imgs = ReportImages.objects.filter(report_id=report_id)

    return render(
        request,
        "report.html.dj",
        {
            "permissions": permissions,
            "report_id": report_id,
            "report": report,
            "favorite": favorite,
            "imgs": imgs,
        },
    )


@login_required
def comments(request, report_id):
    return HttpResponse("comments.")


@login_required
def maint_status(request, report_id):
    return HttpResponse("comments.")


@login_required
def image(request, report_id, image_id):

    img = ReportImages.objects.get(report_id=report_id, image_id=image_id)

    response = HttpResponse(img.image_data, content_type="application/octet-stream")
    response["Content-Disposition"] = 'attachment; filename="%s.png"' % img.image_id

    return response
