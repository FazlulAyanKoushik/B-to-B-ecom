from rest_framework.generics import CreateAPIView

from core.rest.serializers.auth import UserLoginSerializer


class UserLoginView(CreateAPIView):
    serializer_class = UserLoginSerializer
