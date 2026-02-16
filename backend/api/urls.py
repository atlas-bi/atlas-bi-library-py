from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .api import (
    CollectionReportViewSet,
    CollectionTermViewSet,
    CollectionViewSet,
    ReportSearchView,
    TermSearchView,
    UserViewSet,
)

router = routers.DefaultRouter()
router.register("users", UserViewSet, basename="api-users")
router.register("collections", CollectionViewSet, basename="api-collections")
router.register(
    "collection-reports", CollectionReportViewSet, basename="api-collection-reports"
)
router.register(
    "collection-terms", CollectionTermViewSet, basename="api-collection-terms"
)

urlpatterns = [
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
    ),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/search/reports/", ReportSearchView.as_view(), name="api-search-reports"),
    path("api/search/terms/", TermSearchView.as_view(), name="api-search-terms"),
    path("api/", include(router.urls)),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="/api/", permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
