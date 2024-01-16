from django.urls import path, include

from rest_framework_simplejwt.views import TokenVerifyView

from ..views import password

urlpatterns = [
    path("/token", include("core.rest.urls.token")),
    path("/token/verify", TokenVerifyView.as_view(), name="token_verify"),
    path(
        "/password/reset", password.GlobalPasswordReset.as_view(), name="password_reset"
    ),
    path(
        "/password/forget",
        password.GlobalPasswordForget.as_view(),
        name="password_forget",
    ),
    path("", include("core.rest.urls.register_login")),
]
