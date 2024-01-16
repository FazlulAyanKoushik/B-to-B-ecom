from django.contrib.auth import get_user_model
from django.db.models import Case, When, Value, CharField
from django.shortcuts import get_object_or_404

from rest_framework.exceptions import NotFound

from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
)

from accountio.models import Organization, OrganizationUser
from accountio.choices import OrganizationUserRole

from addressio.models import District

from catalogio.models import Category

from .. import permissions
from ..serializers.basic import PrivateBasicCategorySerializer
from ..serializers.organizations import (
    PrivateOrganizationDetailSerializer,
    PrivateOrganizationInfoSerializer,
    PrivateAddressDistrictSerializer,
    PrivateOrganizationSerializer,
)

User = get_user_model()


class PrivateAddressDistrictList(ListAPIView):
    queryset = District.objects.filter().order_by("-name")
    serializer_class = PrivateAddressDistrictSerializer
    permission_classes = [permissions.IsOrganizationStaff]


class PrivateOrganizationInfoDetail(RetrieveAPIView):
    serializer_class = PrivateOrganizationInfoSerializer
    permission_classes = [permissions.IsOrganizationStaff]

    def get_object(self):
        user: User = self.request.user
        try:
            organization_user: OrganizationUser = (
                user.organizationuser_set.select_related("organization")
                .filter()
                .get(is_default=True)
            )
        except OrganizationUser.DoesNotExist:
            raise NotFound(detail="Active organization can not found")

        # extra information added for organization
        user.organization_name = organization_user.organization.name
        user.organization_domain = organization_user.organization.domain
        user.organization_uid = organization_user.organization.uid

        return user


class PrivateOrganizationDetail(RetrieveUpdateAPIView):
    queryset = Organization.objects.get_status_editable()
    serializer_class = PrivateOrganizationDetailSerializer

    def check_permissions(self, request):
        try:
            user, uid, _ = (
                self.request.user,
                self.kwargs.get("uid"),
                self.request.user.get_organization(),
            )

            organization = (
                OrganizationUser.objects.select_related("organization")
                .filter(user=user)
                .values("organization__uid", "role")
                .get(organization__uid=uid)
            )

            if (request.method == "PUT" or request.method == "PATCH") and not (
                organization["role"] == OrganizationUserRole.ADMIN
                or organization["role"] == OrganizationUserRole.OWNER
            ):
                raise ValueError()
        except:
            self.permission_denied(
                request,
                message="You do not have permission to do this action",
            )

    def get_object(self):
        return get_object_or_404(self.queryset, uid=self.kwargs.get("uid"))


class PrivateProductCategoriesList(ListAPIView):
    permission_classes = [permissions.IsOrganizationStaff]
    serializer_class = PrivateBasicCategorySerializer
    pagination_class = None

    def get_queryset(self):
        return (
            Category.objects.prefetch_related(
                "baseproduct_set__get_products__organization"
            )
            .filter(
                baseproduct__get_products__organization=self.request.user.get_organization()
            )
            .order_by("-name")
            .distinct()
        )


class PrivateOrganizationList(ListCreateAPIView):
    serializer_class = PrivateOrganizationSerializer
    pagination_class = None

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsOrganizationAdmin()]
        else:
            return [permissions.IsOrganizationStaff()]

    def get_queryset(self):
        user = self.request.user
        return (
            Organization.objects.prefetch_related("organizationuser_set", "address_set")
            .filter(organizationuser__user=user)
            .annotate(
                role=Case(
                    When(organizationuser__user=user, then="organizationuser__role"),
                    default=Value(
                        ""
                    ),  # Set a default value if the user is not associated with the organization
                    output_field=CharField(),
                )
            )
            .order_by("-name")
        )
