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
    InitiativeViewSet,
    ReportSearchView,
    TermSearchView,
    UserViewSet,
)

router = routers.DefaultRouter()
router.register("users", UserViewSet, basename="api-users")
router.register("initiatives", InitiativeViewSet, basename="api-initiatives")
router.register("collections", CollectionViewSet, basename="api-collections")
router.register(
    "collection-reports", CollectionReportViewSet, basename="api-collection-reports"
)
router.register(
    "collection-terms", CollectionTermViewSet, basename="api-collection-terms"
)

api_urlpatterns = [
    path("", RedirectView.as_view(url="/admin/", permanent=False)),
    path("", include(router.urls)),
    path("schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("search/reports/", ReportSearchView.as_view(), name="api-search-reports"),
    path("search/terms/", TermSearchView.as_view(), name="api-search-terms"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

urlpatterns = [
    path("api/", include(api_urlpatterns)),
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="/admin/", permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
