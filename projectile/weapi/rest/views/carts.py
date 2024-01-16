import logging
from decimal import Decimal

from django.db.models import Prefetch, F
from rest_framework.generics import (
    get_object_or_404,
    DestroyAPIView,
    CreateAPIView,
    RetrieveAPIView,
)
from rest_framework.response import Response

from accountio.utils import get_subdomain

from catalogio.choices import ProductStatus

from catalogio.models import Product

from orderio.models import Cart

from ..permissions import IsOrganizationCustomer
from ..serializers.carts import (
    PrivateCartsSerializer,
    PrivateCartProductSerializer,
)

logger = logging.getLogger(__name__)


class PrivateCartList(CreateAPIView, RetrieveAPIView, DestroyAPIView):
    permission_classes = [IsOrganizationCustomer]
    serializer_class = PrivateCartsSerializer

    def get_object(self):
        organization = get_subdomain(self.request)
        organization_user = organization.organizationuser_set.get(
            user=self.request.user
        )

        # start
        discount_offset = organization_user.discount_offset

        products = (
            Product.objects.get_status_active()
            .select_related(
                "organization",
                "base_product__category",
                "base_product__manufacturer",
                "base_product__brand",
                "base_product__route_of_administration",
                "base_product__medicine_physical_state",
            )
            .prefetch_related(
                "base_product__active_ingredients",
                "mediaimageconnector_set__image",
                "tagconnector_set__tag",
            )
            .annotate(
                total_discount=F("discount_price") + discount_offset,
                final_price_with_offset=F("selling_price")
                * (1 - F("total_discount") / Decimal(100)),
            )
            .filter(organization=organization)
            .order_by("base_product__name")
        )
        # end

        try:
            cart = (
                Cart.objects.prefetch_related(
                    Prefetch("products__product", queryset=products),
                )
                .select_related("organization")
                .get(customer=self.request.user, organization=organization)
            )
            cart.discount_offset = organization_user.discount_offset
            return cart
        except Cart.DoesNotExist:
            return Response(status=200)


class PrivateCartDetail(DestroyAPIView):
    serializer_class = PrivateCartProductSerializer
    permission_classes = [IsOrganizationCustomer]
    queryset = Product.objects.get_status_editable()

    def get_object(self):
        organization = get_subdomain(self.request)
        product = get_object_or_404(
            self.queryset.filter(organization=organization),
            slug=self.kwargs.get("product_slug"),
        )
        cart_product = get_object_or_404(
            Cart.objects.prefetch_related("products")
            .get(customer=self.request.user, organization=organization)
            .products,
            product=product,
        )
        return cart_product
