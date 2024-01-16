from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import AllowAny

from accountio.models import Organization, OrganizationUser
from accountio.utils import get_subdomain

from addressio.models import Address

from weapi.rest import permissions
from weapi.rest.serializers.addresses import (
    PrivateAddressesListDetailSerializer,
    GlobalOrganizationFromDomainSerializer,
)
from weapi.rest.serializers.organizations import PrivateOrganizationDetailSerializer

User = get_user_model()


class PrivateOrganizationDetail(RetrieveAPIView):
    queryset = Organization.objects.get_status_editable()
    serializer_class = PrivateOrganizationDetailSerializer
    permission_classes = [permissions.IsOrganizationStaff]

    def check_permissions(self, request):
        user, slug = (
            self.request.user,
            self.kwargs.get("slug"),
        )
        try:
            OrganizationUser.objects.filter(user=user).get(organization__slug=slug)
        except OrganizationUser.DoesNotExist:
            self.permission_denied(
                request,
                message="You do not have permission to do this action",
            )

    def get_object(self):
        return get_object_or_404(self.queryset, slug=self.kwargs.get("slug"))


class PrivateOrganizationAddressList(ListAPIView):
    permission_classes = [
        permissions.IsOrganizationCustomer | permissions.IsOrganizationStaff
    ]
    serializer_class = PrivateAddressesListDetailSerializer

    def get_queryset(self):
        organization: Organization = get_subdomain(self.request)
        return Address.objects.select_related(
            "upazila", "district", "division", "organization"
        ).filter(organization=organization)


class GlobalOrganizationFromDomainDetail(RetrieveAPIView):
    serializer_class = GlobalOrganizationFromDomainSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        organization: Organization = get_subdomain(self.request)
        return organization
