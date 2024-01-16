from drf_spectacular.utils import extend_schema

from rest_framework.generics import (
    get_object_or_404,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from addressio.choices import AddressStatus
from addressio.models import Address

from .. import permissions
from ..permissions import IsOrganizationCustomer, IsOrganizationStaff
from ..serializers.addresses import PrivateAddressesListDetailSerializer


class PrivateCustomerAddressList(ListCreateAPIView):
    serializer_class = PrivateAddressesListDetailSerializer
    permission_classes = [IsOrganizationStaff | IsOrganizationCustomer]
    queryset = Address.objects.select_related(
        "district", "division", "upazila"
    ).get_status_editable()
    pagination_class = None

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-created_at")


class PrivateCustomerAddressDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = PrivateAddressesListDetailSerializer
    permission_classes = [IsOrganizationCustomer]
    queryset = Address.objects.select_related(
        "district", "division", "upazila"
    ).get_status_editable()

    def get_object(self):
        return get_object_or_404(
            self.queryset.filter(),
            uid=self.kwargs.get("uid"),
        )

    def perform_destroy(self, instance):
        instance.status = AddressStatus.REMOVED
        instance.save()


@extend_schema(responses=PrivateAddressesListDetailSerializer)
class PrivateOrganizationAddressList(ListCreateAPIView):
    permission_classes = [permissions.IsOrganizationStaff]
    serializer_class = PrivateAddressesListDetailSerializer
    pagination_class = None

    def get_queryset(self):
        return (
            Address.objects.select_related(
                "division", "district", "upazila", "organization"
            )
            .filter(organization=self.request.user.get_organization())
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.get_organization())


class PrivateOrganizationAddressDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsOrganizationStaff]
    serializer_class = PrivateAddressesListDetailSerializer

    def get_object(self):
        return get_object_or_404(
            Address.objects.select_related(
                "district", "division", "upazila", "organization"
            ).filter(organization=self.request.user.get_organization()),
            uid=self.kwargs.get("uuid"),
        )

    def perform_destroy(self, instance: Address):
        instance.status = AddressStatus.REMOVED
        instance.save_dirty_fields()
