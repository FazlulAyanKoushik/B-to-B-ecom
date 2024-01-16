from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # Core Private
    path("api/v1/me", include("core.rest.urls.me")),
    # registration
    path("api/v1/auth", include("core.rest.urls.auth")),
    # products
    path("api/v1/products", include("catalogio.rest.urls")),
    # organizations
    path("api/v1/organizations", include("accountio.rest.urls.organizations")),
    # Domains
    path("api/v1/domains", include("accountio.rest.urls.subdomains")),
    # Address
    path("api/v1/address", include("addressio.rest.urls.addresses")),
    # Payments
    path("api/v1/payments", include("paymentio.rest.urls.payments")),
    # verify otp
    path("api/v1/otp", include("otpio.rest.urls.otp")),
    # we private
    path("api/v1/we", include("weapi.rest.urls")),
    # Review
    path("api/v1/reviews", include("reviewio.rest.urls.reviews")),
    # user notification
    path("api/v1/notifications", include("notificationio.rest.urls")),
    # Swagger
    path("api/schema", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"
    ),
    path(
        "api/docs/redoc", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
    path("api-auth/", include("rest_framework.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns.append(path("__debug__", include("debug_toolbar.urls")))
