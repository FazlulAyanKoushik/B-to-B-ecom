from django.contrib.auth import get_user_model

from phonenumber_field.serializerfields import PhoneNumberField

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from otpio.models import UserPhoneOTP

User = get_user_model()


class GlobalPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, write_only=True)
    new_password = serializers.CharField(max_length=255, write_only=True)
    confirm_password = serializers.CharField(max_length=255, write_only=True)

    def validate_new_password(self, new_password):
        password = self.initial_data.get("password")
        if new_password == password:
            raise ValidationError(
                "New password cannot be same as your previous password."
            )
        return new_password

    def validate_confirm_password(self, confirm_password):
        new_password = self.initial_data.get("new_password")
        if new_password != confirm_password:
            raise ValidationError(
                "New password does not match to the confirmation password."
            )
        return confirm_password

    def validate(self, data):
        password = data.get("password")

        if not self.instance.check_password(password):
            raise ValidationError({"detail": "Invalid old password"})

        return data

    def update(self, instance, validated_data):
        new_password = validated_data.pop("new_password")
        instance.set_password(new_password)
        instance.save()
        return instance


class GlobalPasswordForgotSerializer(serializers.Serializer):
    phone = PhoneNumberField(write_only=True)
    otp = serializers.CharField(write_only=True)
    new_password = serializers.CharField(max_length=255, write_only=True)
    confirm_password = serializers.CharField(max_length=255, write_only=True)

    def validate(self, attrs):
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")
        if new_password != confirm_password:
            raise ValidationError(
                {
                    "confirm_password": "New password does not match the confirmation password."
                }
            )
        return attrs

    def create(self, validated_data):
        user = get_object_or_404(
            User.objects.filter(),
            phone=validated_data.get("phone"),
        )
        user_otp = get_object_or_404(
            UserPhoneOTP.objects.filter(), user=user, otp=validated_data.get("otp")
        )
        if user and user_otp:
            new_password = validated_data.pop("new_password")
            user.set_password(new_password)
            user.save()
            return validated_data
        else:
            raise ValidationError({"otp": "Invalid otp"})
