from django.urls import reverse


def verify_otp_url():
    return reverse("verify-otp")


def resend_otp_url():
    return reverse("resend-otp")
