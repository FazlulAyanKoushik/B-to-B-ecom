from django.contrib.auth import get_user_model

from phonenumber_field.serializerfields import PhoneNumberField

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from core.utils import create_token

from otpio.utils.otp import OTP
from otpio.models import UserPhoneOTP

User = get_user_model()


class ResendOtpSerializer(serializers.Serializer):
    phone = serializers.CharField()

    def create(self, validated_data):
        user = get_object_or_404(
            User.objects.filter(), phone=validated_data.get("phone")
        )
        otp = OTP()
        otp, send_sms = otp.save_otp_and_send_sms(
            phone=validated_data.get("phone"), user=user
        )
        if not send_sms:
            raise ValidationError({"detail": "SMS cannot be send."})

        return validated_data


class CreateOTPSerializer(serializers.Serializer):
    otp = serializers.CharField()

    def create(self, validated_data):
        user = self.context["request"].user
        otp = OTP()
        user_otp = otp.generate_unique_otp()
        UserPhoneOTP.objects.create(user=user, otp=user_otp)
        return validated_data


class VerifyOTPSerializer(serializers.Serializer):
    otp = serializers.CharField()

    def create(self, validated_data):
        user_phone_otp = get_object_or_404(
            UserPhoneOTP.objects.filter(), otp=validated_data.get("otp")
        )
        if not user_phone_otp.is_expired():
            user_phone_otp.is_status_consumed()
            return validated_data
        else:
            raise ValidationError("OTP Expired.")


class VerifyOTPWithTokenSerializer(serializers.Serializer):
    otp = serializers.CharField(write_only=True)

    def validate_otp(self, value):
        user_phone_otp = get_object_or_404(UserPhoneOTP.objects.filter(), otp=value)
        if not user_phone_otp.is_expired():
            user_phone_otp.is_status_consumed()
            access_token, refresh_token = create_token(user_phone_otp.user)
            return {"access": access_token, "refresh": refresh_token}
        else:
            raise ValidationError({"otp": "Invalid otp"})
