"""atlas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import logging
from typing import Any, Dict

import djangosaml2
from django.conf import settings as django_settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import include, path, re_path
from django.utils import timezone
from index.models import AnalyticsErrors

logger = logging.getLogger(__name__)

urlpatterns = [
    path("", include("index.urls")),
    path("saml2/", include("djangosaml2.urls")),
    path("test/", djangosaml2.views.EchoAttributesView.as_view()),
    path("mail/", include("mail.urls")),
    path("analytics/", include("analytics.urls")),
    path("reports/", include("report.urls")),
    path("initiatives/", include("initiative.urls")),
    path("terms/", include("term.urls")),
    path("users/", include("user.urls")),
    path("search/", include("search.urls")),
    path("collections/", include("collection.urls")),
    path("etl/", include("etl.urls")),
    path("profile/", include("sketch.urls")),
    path("settings/", include("settings.urls")),
    path("groups/", include("group.urls")),
    path("tasks/", include("task.urls")),
]


# if in dev or test use local auth
if (
    getattr(django_settings, "DEBUG", False)
    or getattr(django_settings, "TESTING", False)
    or getattr(django_settings, "DEMO", False)
):
    urlpatterns.append(path("accounts/", include("django.contrib.auth.urls")))

if getattr(django_settings, "DEBUG", False):
    import debug_toolbar

    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)

# if running test server, enable static urls
if getattr(django_settings, "TESTING", False):
    import os
    import posixpath

    from django.contrib.staticfiles import finders
    from django.http import Http404
    from django.views import static

    def serve(
        request: HttpRequest,
        path: str,
        insecure: bool = False,
        **kwargs: Dict[Any, Any]
    ) -> Any:
        """Custom static file serve to ignore debug flag."""
        normalized_path = posixpath.normpath(path).lstrip("/")
        absolute_path = finders.find(normalized_path)
        if not absolute_path:
            if path.endswith("/") or path == "":
                raise Http404("Directory indexes are not allowed here.")
            raise Http404("'%s' could not be found" % path)
        document_root, path = os.path.split(absolute_path)
        return static.serve(request, path, document_root=document_root, **kwargs)

    urlpatterns += [
        re_path(r"^static/(?P<path>.*)$", serve),
    ]


import sys
import traceback


def full_stack() -> str:
    """Return full stack trace of an exception.

    :returns: full stack trace of an exception.
    """
    exc = sys.exc_info()[0]
    if exc is not None:
        frame = sys.exc_info()[-1].tb_frame.f_back  # type: ignore[union-attr]
        stack = traceback.extract_stack(frame)
    else:
        stack = traceback.extract_stack()[:-1]  # type: ignore[assignment]  # last one would be full_stack()
    trc = "Traceback (most recent call last):\n"
    stackstr = trc + "".join(traceback.format_list(stack))
    if exc is not None:
        # pylint: disable=bad-str-strip-call
        stackstr += "  " + traceback.format_exc().lstrip(trc)
    return stackstr


def custom_error_view(request: HttpRequest, exception: Any = None) -> HttpResponse:
    """Log 500 errors."""

    AnalyticsErrors(
        user=request.user if not request.user.is_anonymous else None,
        status_code=404,
        referer=request.META.get("HTTP_REFERER"),
        useragent=request.headers.get("User-Agent"),
        message=exception,
        access_date=timezone.now(),
        trace=full_stack(),
    ).save()
    logger.error(full_stack())
    logger.warning(exception)
    return render(
        request,
        "error.html.dj",
        context={"message": "Sorry an error occurred while accessing that page."},
        status=200,
    )


def custom_warning_view(request: HttpRequest, exception: Any = None) -> HttpResponse:
    """Log 400 errors."""
    AnalyticsErrors(
        user=request.user if not request.user.is_anonymous else None,
        status_code=404,
        referer=request.META.get("HTTP_REFERER"),
        useragent=request.headers.get("User-Agent"),
        message=exception,
        access_date=timezone.now(),
    ).save()

    logger.warning(full_stack())
    logger.warning(exception)

    return render(
        request,
        "error.html.dj",
        context={"message": "Sorry that page could not be found."},
        status=404,
    )


handler500 = custom_error_view
handler404 = custom_warning_view
