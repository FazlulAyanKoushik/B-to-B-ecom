from rest_framework.generics import (
    get_object_or_404,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)


from accountio.models import Organization, OrganizationUser
from accountio.utils import get_subdomain
from accountio.choices import OrganizationUserRole

from weapi.rest import permissions

from ..serializers.reviews import ReviewSerializer

from ...models import Review


class GlobalReviewListView(ListCreateAPIView):
    serializer_class = ReviewSerializer

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
                organization["role"] == OrganizationUserRole.CUSTOMER
            ):
                raise ValueError()

        except:
            self.permission_denied(
                request,
                message="You do not have permission to do this action",
            )


    def get_queryset(self):
        organization: Organization = get_subdomain(self.request)
        queryset = Review.objects.filter(organization=organization)
        target = self.request.query_params.get("target")
        if target == "product":
            return queryset.filter(product__isnull=False)
        elif target == "order":
            return queryset.filter(order__isnull=False)
        else:
            return queryset

    def perform_create(self, serializer):
        serializer.save(given_by=self.request.user)


class GlobalReviewDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsOrganizationCustomer()]
        return [
            permissions.IsOrganizationStaff() or permissions.IsOrganizationCustomer()
        ]

    def get_object(self):
        uid = self.kwargs.get("uid")
        review = get_object_or_404(Review.objects.filter(), uid=uid)
        return review
