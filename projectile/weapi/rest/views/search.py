from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from catalogio.models import Product

from redisio.services.base_products import BaseProductRedisServices

from ..permissions import IsOrganizationCustomer, IsOrganizationStaff
from ..serializers.products import PrivateProductSerializer
from ..serializers.search import PrivateBaseProductSearchSerializer


class PrivateBaseProductSearch(ListAPIView):
    serializer_class = PrivateBaseProductSearchSerializer
    permission_classes = [IsOrganizationStaff]

    def get_queryset(self):
        return None

    def get(self, request, *args, **kwargs):
        search = self.request.query_params.get("search", "")
        if not search:
            return Response(status=status.HTTP_204_NO_CONTENT)

        base_product_search = BaseProductRedisServices()
        search_products = base_product_search.search_by_base_product_name(name=search)
        return Response(data=search_products)


@extend_schema(
    description="You can search merchant product here. Example: http://127.0.0.1:8000/api/v1/we/search/merchant/products?categories=analgesics&categories=analgesics2&dosage-form=oral&manufacturer=manufacturers3&active-ingredients=minoxidil&active-ingredients=minoxidil1",
    parameters=[
        OpenApiParameter(
            "manufacturer",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="single manufacturer slug only URL?manufacturer=manufacturer1",
        ),
        OpenApiParameter(
            "category",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="Single category slug ex: URL?category=category1",
        ),
        OpenApiParameter(
            "dosage-form",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="Single dosage-form name only ex: URL?dosage-form=oral",
        ),
        OpenApiParameter(
            "active-ingredients",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="Multiple active-ingredients name only ex: URL?active-ingredients=minoxidil&active-ingredients=minoxidil1",
        ),
    ],
)
class PrivateProductSearch(ListAPIView):
    serializer_class = PrivateProductSerializer
    queryset = Product.objects.get_status_editable()
    permission_classes = [IsOrganizationCustomer]
    filter_backends = [SearchFilter]
    search_fields = [
        "base_product__name",
        "organization__name",
        "base_product__category__name",
        "base_product__active_ingredients__name",
        "base_product__manufacturer__name",
        "base_product__brand__name",
        "base_product__description",
        "base_product__unit",
        "base_product__strength",
    ]

    def get_queryset(self):
        products = (
            self.queryset.select_related(
                "base_product",
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
            .filter(organization=self.request.user.get_organization())
            .order_by("base_product__name")
        )
        # filter by category
        category = self.request.query_params.get("category", "")
        if category:
            products = products.filter(base_product__category__slug=category)

        # filter by dosage form
        dosage_form = self.request.query_params.get("dosage-form", "")
        if dosage_form:
            products = products.filter(base_product__dosage_form__icontains=dosage_form)

        # filter by manufacturer
        manufacturer = self.request.query_params.get("manufacturer", "")
        if manufacturer:
            products = products.filter(base_product__manufacturer__slug=manufacturer)

        # filter by active-ingredients
        active_ingredients = self.request.query_params.getlist(
            "active-ingredients", [""]
        )
        if active_ingredients[0]:
            products = products.filter(
                base_product__active_ingredients__slug__in=active_ingredients
            )

        return products
