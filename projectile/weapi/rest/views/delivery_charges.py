from rest_framework.exceptions import NotFound

from addressio.models import Address, District

from catalogio.models import DeliveryCharge

from rest_framework.generics import (
    get_object_or_404,
    ListCreateAPIView,
    RetrieveUpdateAPIView,
)

from accountio.choices import OrganizationUserRole
from accountio.models import OrganizationUser, Organization
from accountio.utils import get_subdomain

from ..serializers.orders import (
    PrivateDeliveryChargeListSerializers,
    PrivateDeliveryChargeSerializers,
)

from rest_framework.response import Response


class PrivateDeliveryChargeList(ListCreateAPIView):
    serializer_class = PrivateDeliveryChargeListSerializers

    def check_permissions(self, request):
        try:
            user, org = (
                self.request.user,
                get_subdomain(self.request),
            )
            organization = (
                OrganizationUser.objects.select_related("organization")
                .filter(user=user)
                .values("organization", "role")
                .get(organization=org)
            )
            if self.request.method == "POST" and not (
                organization["role"] == OrganizationUserRole.ADMIN
                or organization["role"] == OrganizationUserRole.OWNER
            ):
                raise ValueError()

        except:
            self.permission_denied(
                request,
                message="You do not have permission to do this action",
            )

    def get_queryset(self):
        organization = get_subdomain(self.request)

        delivery_charge = DeliveryCharge.objects.select_related("district").filter(
            organization=organization
        )

        return delivery_charge


class PrivateDeliveryCharge(RetrieveUpdateAPIView):
    serializer_class = PrivateDeliveryChargeSerializers

    def check_permissions(self, request):
        try:
            user, org = (
                self.request.user,
                get_subdomain(self.request),
            )
            organization = (
                OrganizationUser.objects.select_related("organization")
                .filter(user=user)
                .values("organization", "role")
                .get(organization=org)
            )
            if self.request.method in ["PUT", "PATCH"] and not (
                organization["role"]
                in [
                    OrganizationUserRole.ADMIN,
                    OrganizationUserRole.OWNER,
                    OrganizationUserRole.MANAGER,
                    OrganizationUserRole.STAFF,
                ]
            ):
                raise ValueError()

        except:
            self.permission_denied(
                request,
                message="You do not have permission to do this action",
            )

    def get_object(self):
        address_uid = self.kwargs.get("address_uid", None)

        # get organization from url
        organization: Organization = get_subdomain(self.request)

        # get district
        district: District = get_object_or_404(
            Address.objects.filter(), uid=address_uid
        ).district

        # get delivery charge
        try:
            charge = DeliveryCharge.objects.get(
                district=district, organization=organization
            )
        except DeliveryCharge.DoesNotExist:
            if self.request.method == "GET":
                charge = organization.delivery_charge
            else:
                raise NotFound()

        return {"charge": charge}
