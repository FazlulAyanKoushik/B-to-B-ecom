from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.rest.views import auth

urlpatterns = [
    path("/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    # path("/logout", otp.GlobalLogoutView.as_view(), name="logout"),
    # path("", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("", auth.UserLoginView.as_view(), name="token_obtain_pair"),
]
