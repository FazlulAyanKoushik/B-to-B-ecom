from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.generics import get_object_or_404, CreateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import create_token

from otpio.models import UserPhoneOTP
from otpio.rest.serializers.otp import (
    ResendOtpSerializer,
    CreateOTPSerializer,
    VerifyOTPSerializer,
)

User = get_user_model()


class VerifyUserOTP(APIView):
    def put(self, request):
        user_phone_otp = get_object_or_404(
            UserPhoneOTP.objects.filter(), otp=request.data["otp"]
        )
        if not user_phone_otp.is_expired():
            user_phone_otp.is_status_consumed()
            user_phone_otp.save()
            access_token, refresh_token = create_token(user_phone_otp.user)
            return Response(
                {"access": access_token, "refresh": refresh_token},
                status=status.HTTP_200_OK,
            )
        else:
            raise APIException(code=400, detail="OTP Expired.")


class ResendUserOTP(CreateAPIView):
    serializer_class = ResendOtpSerializer


class CreateUserOTP(CreateAPIView):
    serializer_class = CreateOTPSerializer


class VerifyUsersOTP(UpdateAPIView):
    serializer_class = VerifyOTPSerializer
    http_method_names = ["put"]

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)
