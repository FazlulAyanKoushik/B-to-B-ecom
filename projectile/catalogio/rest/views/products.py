from decimal import Decimal

from django.db.models import F

from django_filters.rest_framework import DjangoFilterBackend

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
)

from rest_framework import (
    generics,
    filters,
)

from accountio.utils import get_subdomain

from catalogio.models import Product

from weapi.rest.filters.products import FilterProducts
from weapi.rest.permissions import IsOrganizationCustomer

from ..serializers.products import GlobalProductSerializer
from ...choices import ProductStatus


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(name="category", description="Category slug", type=str),
            OpenApiParameter(
                name="dosage-form", description="Dosage-Form slug", type=str
            ),
            OpenApiParameter(
                name="manufacturer", description="Manufacturer slug", type=str
            ),
            OpenApiParameter(
                name="final_price_min",
                description="Min Final Price",
                type=Decimal,
            ),
            OpenApiParameter(
                name="final_price_max",
                description="Max Final Price",
                type=Decimal,
            ),
            OpenApiParameter(
                name="search",
                description="Search by product name, tag name.",
                type=str,
            ),
        ]
    )
)
class GlobalProductSearchList(generics.ListAPIView):
    serializer_class = GlobalProductSerializer
    permission_classes = [IsOrganizationCustomer]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = [
        "base_product__name",
        "base_product__unit",
        "tagconnector__tag__name",
    ]
    filterset_class = FilterProducts

    def get_queryset(self):
        organization = get_subdomain(self.request)
        discount_offset = organization.organizationuser_set.get(
            user=self.request.user
        ).discount_offset

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
        # filter by category
        category = self.request.query_params.get("category", "")
        if category:
            products = products.filter(base_product__category__slug=category)

        # filter by dosage form
        dosage_form = self.request.query_params.get("dosage-form", "")
        if dosage_form:
            products = products.filter(base_product__dosage_form__slug=dosage_form)

        # filter by manufacturer
        manufacturer = self.request.query_params.get("manufacturer", "")
        if manufacturer:
            products = products.filter(base_product__manufacturer__slug=manufacturer)

        return products


class GlobalProductDetail(generics.RetrieveAPIView):
    serializer_class = GlobalProductSerializer
    permission_classes = [IsOrganizationCustomer]
    lookup_field = "slug"

    def get_queryset(self):
        organization = get_subdomain(self.request)
        discount_offset = organization.organizationuser_set.get(
            user=self.request.user
        ).discount_offset
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
            )
            .annotate(
                total_discount=F("discount_price") + discount_offset,
                final_price_with_offset=F("selling_price")
                * (1 - F("total_discount") / Decimal(100)),
            )
            .filter(organization=organization)
        )

        return products
