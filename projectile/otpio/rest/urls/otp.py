from django.urls import path
from ..views import otp


urlpatterns = [
    # path("/verify", otp.VerifyUserOTP.as_view(), name="verify-otp"),
    path("/send", otp.ResendUserOTP.as_view(), name="resend-otp"),
    # path("/verify/only", otp.VerifyUsersOTP.as_view(), name="otp-verify-only"),
    # path("", otp.CreateUserOTP.as_view(), name="create-otp"),
]
