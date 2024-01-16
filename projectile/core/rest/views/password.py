from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.rest.serializers.password import (
    GlobalPasswordResetSerializer,
    GlobalPasswordForgotSerializer,
)


class GlobalPasswordReset(UpdateAPIView):
    serializer_class = GlobalPasswordResetSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["put"]

    def get_object(self):
        return self.request.user


class GlobalPasswordForget(UpdateAPIView):
    serializer_class = GlobalPasswordForgotSerializer
    http_method_names = ["put"]

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)
