from decimal import Decimal

from django.db.models import Count, Sum, Prefetch, F

from django_filters.rest_framework import DjangoFilterBackend

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
)

from rest_framework import filters
from rest_framework.generics import (
    get_object_or_404,
    RetrieveUpdateAPIView,
    ListCreateAPIView,
    UpdateAPIView,
)

from orderio.choices import OrderStageChoices, OrderDeliveryStatus
from orderio.models import Order, OrderDelivery, OrderProduct

from ..filters.orders import FilterOrders
from ..permissions import IsOrganizationStaff, IsOrganizationAdmin
from ..serializers.orders import (
    PrivateOrderListSerializers,
    PrivateOrderDetailSerializer,
    PrivateReturnProductHoldSerializer,
)


@extend_schema_view(
    get=extend_schema(
        description="URL: /api/v1/we/orders?date_before=2023-04-09&date_after=2023-04-09&status=PROCESSING",
        parameters=[
            OpenApiParameter(
                "total_price_min",
                OpenApiTypes.DECIMAL,
                OpenApiParameter.QUERY,
                description="Filter by total price minimum",
            ),
            OpenApiParameter(
                "total_price_max",
                OpenApiTypes.DECIMAL,
                OpenApiParameter.QUERY,
                description="Filter by total price maximum",
            ),
            OpenApiParameter(
                "date_before, format: year(2022)-month(02)-date(15)",
                OpenApiTypes.DATE,
                OpenApiParameter.QUERY,
                description="Filter order by date. It will execute the query before from the provided date. Date format=2016-01-01",
            ),
            OpenApiParameter(
                "date_after",
                OpenApiTypes.DATE,
                OpenApiParameter.QUERY,
                description="Filter order by date. It will execute the query after from the provided date with provided date. Date format=2016-01-01",
            ),
            OpenApiParameter(
                "status",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Example use proper STATUS choice. "
                + ", ".join(OrderDeliveryStatus.values),
            ),
            OpenApiParameter(
                name="search",
                description="Search by customer first name, last name, phone, Order id, Address label, house street, upazila, division, district and country",
                type=str,
            ),
        ],
    )
)
@extend_schema(
    description="The order list can be viewed by admin, owner, manager, and staff. Admin or owner have the ability to create a order for customer"
)
class PrivateOrderList(ListCreateAPIView):
    serializer_class = PrivateOrderListSerializers
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = [
        "customer__first_name",
        "customer__last_name",
        "customer__phone",
        "serial_number",
        "address__label",
        "address__house_street",
        "address__upazila",
        "address__division",
        "address__country",
        "address__district",
    ]
    filterset_class = FilterOrders

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsOrganizationAdmin()]

        return [IsOrganizationStaff()]

    def get_queryset(self):
        orders = (
            Order.objects.select_related("customer", "organization")
            .prefetch_related(
                "delivery_statuses",
            )
            .filter(organization=self.request.user.get_organization())
            .annotate(
                total_products=Count("order_products", distinct=True),
                returned_total_quantity=Sum(
                    "returnorderproduct__returned_quantity", default=0, distinct=True
                ),
            )
            .order_by("-created_at")
        )
        # checking if status is in query params
        status = self.request.query_params.get("status", "")
        if status:
            orders = orders.filter(
                delivery_statuses__status=status,
                delivery_statuses__stage=OrderStageChoices.CURRENT,
            )

        return orders


@extend_schema(
    description="The order can be viewed by admin, owner, manager, and staff. Admin or owner have the ability to change the order status both forward and backward, while staff can only change the order status forward."
)
class PrivateOrderDetail(RetrieveUpdateAPIView):
    serializer_class = PrivateOrderDetailSerializer
    permission_classes = [IsOrganizationStaff]

    def get_object(self):
        uid = self.kwargs.get("uid")

        order = get_object_or_404(
            Order.objects.select_related("customer")
            .prefetch_related(
                "order_products__product__base_product",
                Prefetch(
                    "delivery_statuses",
                    queryset=OrderDelivery.objects.filter().order_by("stage"),
                ),
                "returnorderproduct_set__product__base_product",
            )
            .filter(organization=self.request.user.get_organization()),
            uid=uid,
        )

        order.partial_return_products = order.returnorderproduct_set.annotate(
            final_price_with_offset=F("order_product__selling_price")
            * (1 - (F("order_product__discount_price") / Decimal(100))),
            total_quantity_price=F("order_product__updated_quantity")
            * F("final_price_with_offset"),
        ).filter(is_return_by_merchant=False)

        order.partial_delivery_products = order.returnorderproduct_set.annotate(
            final_price_with_offset=F("order_product__selling_price")
            * (1 - (F("order_product__discount_price") / Decimal(100))),
            total_quantity_price=F("order_product__updated_quantity")
            * F("final_price_with_offset"),
        ).filter(is_return_by_merchant=True)

        return order


class PrivateRerunOrderProduct(UpdateAPIView):
    serializer_class = PrivateReturnProductHoldSerializer
    permission_classes = [IsOrganizationStaff]
    http_method_names = ["put"]

    def get_object(self):
        kwargs = {
            "uid": self.kwargs["order_uid"],
        }

        order: Order = get_object_or_404(
            Order.objects.filter(organization=self.request.user.get_organization()),
            **kwargs
        )
        return order
