import random

from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework.generics import get_object_or_404

from otpio.models import UserPhoneOTP

from weapi.rest.utils.sms import SMS

User = get_user_model()


class OTP:
    def generate_unique_otp(self, length=settings.OTP_CHARACTER_LENGTH) -> str:
        otp = "".join(random.choices("0123456789", k=length))
        unique_otp = self.check_otp_unique(otp)
        return unique_otp

    def check_otp_unique(self, otp: str):
        exists = UserPhoneOTP.objects.filter(otp=otp).exists()
        if exists:
            otp = self.generate_unique_otp()
        return otp

    def save_otp_and_send_sms(
        self, phone: str, user: User = None, otp: str = None
    ) -> (UserPhoneOTP, bool):
        if otp is None:
            otp = self.generate_unique_otp()

        if user is None:
            user = get_object_or_404(User.objects.filter(), phone=phone)

        user_otp = UserPhoneOTP.objects.create(user=user, otp=otp, is_consumed=False)

        sms = SMS()
        response_sms = sms.send_otp_to_one(recipient=phone, otp=otp)
        if not response_sms:
            user_otp.delete()

        return user_otp, response_sms
