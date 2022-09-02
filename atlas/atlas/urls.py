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

import djangosaml2
from django.conf import settings as django_settings
from django.http import HttpResponse
from django.urls import include, path, re_path

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
]


# if in dev or test use local auth
if (
    hasattr(django_settings, "DEBUG")
    and getattr(django_settings, "DEBUG")
    or hasattr(django_settings, "TESTING")
    and getattr(django_settings, "TESTING")
    or hasattr(django_settings, "DEMO")
    and getattr(django_settings, "DEMO")
):
    urlpatterns.append(path("accounts/", include("django.contrib.auth.urls")))

if hasattr(django_settings, "DEBUG") and getattr(django_settings, "DEBUG"):
    import debug_toolbar

    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)

import sys
import traceback


def full_stack():
    """Return full stack trace of an exception.

    :returns: full stack trace of an exception.
    """
    exc = sys.exc_info()[0]
    if exc is not None:
        frame = sys.exc_info()[-1].tb_frame.f_back
        stack = traceback.extract_stack(frame)
    else:
        stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    trc = "Traceback (most recent call last):\n"
    stackstr = trc + "".join(traceback.format_list(stack))
    if exc is not None:
        # pylint: disable=bad-str-strip-call
        stackstr += "  " + traceback.format_exc().lstrip(trc)
    return stackstr


def custom_error_view(request, exception=None):
    """Log 500 errors."""
    logger.error(full_stack())
    logger.warning(exception)
    return HttpResponse(
        "Ops, there was an error. Please try again in a few minutes.", status=500
    )


def custom_warning_view(request, exception=None):
    """Log 400 errors."""
    logger.warning(full_stack())
    logger.warning(exception)
    return HttpResponse("Ops, that page doesn't exist!", status=404)


handler500 = custom_error_view
handler404 = custom_warning_view
