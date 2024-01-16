from drf_spectacular.utils import extend_schema

from rest_framework.generics import CreateAPIView

from ..serializers.auth import (
    GlobalOrganizationRegisterSerializer,
    GlobalUserRegistrationSerializer,
)


@extend_schema(description="You can register to an organization")
class GlobalUserRegistrationList(CreateAPIView):
    serializer_class = GlobalUserRegistrationSerializer


class GlobalOrganizationRegister(CreateAPIView):
    serializer_class = GlobalOrganizationRegisterSerializer
