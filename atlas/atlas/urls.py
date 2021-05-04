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
import djangosaml2
from django.conf import settings as django_settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    #  path("admin/", admin.site.urls),
    path("", include("index.urls")),
    path("saml2/", include("djangosaml2.urls")),
    path("test/", djangosaml2.views.EchoAttributesView.as_view()),
    path("mail/", include("mail.urls")),
    path("analytics/", include("analytics.urls")),
    path("reports/", include("report.urls")),
    path("initiatives/", include("initiative.urls")),
    path("terms/", include("term.urls")),
    path("user/", include("user.urls")),
    path("search/", include("search.urls")),
    path("projects/", include("project.urls")),
]


# if in dev or test use local auth
if (
    hasattr(django_settings, "DEBUG")
    and getattr(django_settings, "DEBUG")
    or hasattr(django_settings, "TESTING")
    and getattr(django_settings, "TESTING")
):
    urlpatterns.append(path("accounts/", include("django.contrib.auth.urls")))

    import debug_toolbar

    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
