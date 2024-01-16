import decimal
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import (
    Count,
    Sum,
    QuerySet,
    Prefetch,
    F,
)

from django_filters.rest_framework import DjangoFilterBackend

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework.filters import SearchFilter
from rest_framework.generics import (
    get_object_or_404,
    ListCreateAPIView,
    RetrieveAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
)

from accountio.choices import OrganizationUserRole
from accountio.models import TransactionOrganizationUser, Organization, OrganizationUser
from accountio.utils import get_subdomain

from orderio.choices import OrderDeliveryStatus, OrderStageChoices
from orderio.models import Order, ReturnOrderProduct, OrderProduct

from weapi.rest import permissions

from ..filters.orders import FilterOrders
from ..serializers.orders import PrivateCustomerCountByMonthOfAYearSerializers
from ..serializers.orders import (
    PrivateCustomerOrderSerializer,
    OrderCountByStatusSerializer,
)
from ..serializers.organizations import (
    PrivateCustomerSerializer,
    PrivateCustomerDetailSerializer,
    PrivateCustomerTransactionHistoryDetailSerializer,
)
from ..utils.customers import add_customer_extra_role_balance_information

User = get_user_model()


@extend_schema(
    parameters=[
        OpenApiParameter(
            "date_after",
            OpenApiTypes.DATE,
            OpenApiParameter.QUERY,
            description="Search by date only. 2023-01-30. Filter by all data after this date",
        ),
        OpenApiParameter(
            "date_before",
            OpenApiTypes.DATE,
            OpenApiParameter.QUERY,
            description="Search by date only. 2023-01-30. Filter by all data before this date",
        ),
        OpenApiParameter(
            "search",
            OpenApiTypes.UUID,
            OpenApiParameter.QUERY,
            description="Search by product name and order id.",
        ),
        OpenApiParameter(
            "status",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="Filter by "
            + ", ".join(OrderDeliveryStatus.values)
            + " which is in current stage",
        ),
    ],
)
@extend_schema(
    responses=PrivateCustomerOrderSerializer(many=True),
    description="Customer order list",
)
class PrivateCustomerOrderList(ListCreateAPIView):
    permission_classes = [permissions.IsOrganizationCustomer]
    serializer_class = PrivateCustomerOrderSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = FilterOrders
    search_fields = ["order_products__product__base_product__name", "serial_number"]

    def get_queryset(self):
        organization = get_subdomain(self.request)

        orders = (
            Order.objects.select_related("payment_method", "customer", "organization")
            .prefetch_related(
                "delivery_statuses",
                Prefetch(
                    "order_products",
                    queryset=OrderProduct.objects.prefetch_related(
                        "product__base_product"
                    ).annotate(
                        final_price_with_offset=F("selling_price")
                        * (1 - (F("discount_price") / Decimal(100))),
                        total_quantity_price=F("updated_quantity")
                        * F("final_price_with_offset"),
                    ),
                ),
            )
            .filter(organization=organization, customer=self.request.user)
            .annotate(total_products=Count("order_products"))
            .order_by("-created_at")
        )
        # filter by delivery status which is in current stage
        delivery_status = self.request.query_params.get("status", "")
        if delivery_status:
            orders = orders.filter(
                delivery_statuses__status=delivery_status,
                delivery_statuses__stage=OrderStageChoices.CURRENT,
            )
        return orders


@extend_schema(description="Customer order detail")
class PrivateCustomerOrderDetail(RetrieveAPIView):
    serializer_class = PrivateCustomerOrderSerializer
    permission_classes = [permissions.IsOrganizationCustomer]

    def get_object(self):
        organization = get_subdomain(self.request)

        order = get_object_or_404(
            Order.objects.select_related("payment_method")
            .prefetch_related(
                "delivery_statuses",
                Prefetch(
                    "order_products",
                    queryset=OrderProduct.objects.prefetch_related(
                        "product__base_product__active_ingredients"
                    ).annotate(
                        final_price_with_offset=F("selling_price")
                        * (1 - F("discount_price") / Decimal(100)),
                        total_quantity_price=F("updated_quantity")
                        * F("final_price_with_offset"),
                    ),
                ),
                Prefetch(
                    "returnorderproduct_set",
                    to_attr="partial_delivery_products",
                    queryset=ReturnOrderProduct.objects.select_related(
                        "product__base_product"
                    ).filter(is_return_by_merchant=True),
                ),
                Prefetch(
                    "returnorderproduct_set",
                    to_attr="partial_return_products",
                    queryset=ReturnOrderProduct.objects.select_related(
                        "product__base_product"
                    ).filter(is_return_by_merchant=False),
                ),
            )
            .filter(organization=organization, customer=self.request.user)
            .annotate(
                total_products=Count("order_products"),
            ),
            uid=self.kwargs.get("uid"),
        )

        return order


@extend_schema(
    description="Merchant total customers from his current organization. You can filter your customer by status",
    parameters=[
        OpenApiParameter(
            "statuses",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="Multiple statuses name only URL?statuses=ACTIVE&statuses=DRAFT",
        ),
        OpenApiParameter(
            "search",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="Search by first name, last name and phone number",
        ),
        OpenApiParameter(
            "balance",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="filter by balance: advance, due, zero",
        ),
    ],
)
class PrivateCustomerList(ListAPIView):
    serializer_class = PrivateCustomerSerializer
    permission_classes = [permissions.IsOrganizationStaff]

    def get_queryset(self):
        organization: Organization = self.request.user.get_organization()
        users_ids = list(
            organization.organizationuser_set.filter(
                role=OrganizationUserRole.CUSTOMER
            ).values_list("user", flat=True)
        )

        users: QuerySet[User] = (
            User.objects.prefetch_related("organizationuser_set", "orders")
            .filter(id__in=users_ids)
            .order_by("-created_at")
        )

        search = self.request.query_params.get("search", "")
        if len(search):
            search_users_first_name = users.filter(first_name__istartswith=search)
            search_users_last_name = users.filter(last_name__istartswith=search)
            search_users_phone = users.filter(phone__istartswith=search)

            users = (
                search_users_phone | search_users_first_name | search_users_last_name
            ).distinct()

        statuses = self.request.query_params.getlist("statuses", [""])
        if statuses[0]:
            users = users.filter(organizationuser__status__in=statuses)

        # a new filtered variable where i store the filtered value
        filtered_users = []

        for user in users:
            total_pay = (
                user.transactionorganizationuser_set.filter(organization=organization)
                .aggregate(total_payable_money=Sum("payable_money", default=0))
                .get("total_payable_money", Decimal(0))
            )
            total_buy = (
                user.orders.filter(organization=organization)
                .aggregate(total_price=Sum("total_price", default=0))
                .get("total_price", Decimal(0))
            )
            organization_user: OrganizationUser = get_object_or_404(
                user.organizationuser_set, organization=organization
            )

            # Filter by balance
            balance_filter = self.request.query_params.get("balance", "")
            if len(balance_filter):
                balance: decimal.Decimal = total_pay - total_buy

                if (
                    (
                        balance_filter == "advance"
                        and balance.compare(decimal.Decimal(0)) == 1
                    )
                    or (
                        balance_filter == "due"
                        and balance.compare(decimal.Decimal(0)) == -1
                    )
                    or (
                        balance_filter == "zero"
                        and balance.compare(decimal.Decimal(0)) == 0
                    )
                ):
                    filtered_users.append(
                        add_customer_extra_role_balance_information(
                            user=user,
                            organization_user=organization_user,
                            total_buy=total_buy,
                            total_pay=total_pay,
                        )
                    )
                else:
                    continue

            else:
                filtered_users.append(
                    add_customer_extra_role_balance_information(
                        user=user,
                        organization_user=organization_user,
                        total_buy=total_buy,
                        total_pay=total_pay,
                    )
                )

        return filtered_users


@extend_schema(
    description="Merchant organization customer detail who buy products from merchant organization."
)
class PrivateCustomerDetail(RetrieveUpdateAPIView):
    serializer_class = PrivateCustomerDetailSerializer
    http_method_names = ["get", "put", "patch"]

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [permissions.IsOrganizationAdmin()]

        return [permissions.IsOrganizationStaff()]

    def get_object(self):
        organization = self.request.user.get_organization()

        user: User = get_object_or_404(
            User.objects.prefetch_related(
                "organizationuser_set", "address_set"
            ).filter(),
            uid=self.kwargs.get("uid", None),
        )
        org_user = user.organizationuser_set.get(
            organization=organization, role=OrganizationUserRole.CUSTOMER
        )

        total_money = Order.objects.filter(customer=user).aggregate(
            total_money=Sum("total_price")
        )["total_money"]
        total_pay = TransactionOrganizationUser.objects.filter(user=user).aggregate(
            total_pay=Sum("payable_money")
        )["total_pay"]

        user.total_pay = total_money if total_money else 0
        user.total_money = total_pay if total_pay else 0
        user.role = org_user.role
        user.discount_offset = org_user.discount_offset
        user.organization = organization

        return user


class PrivateCustomerCountByMonthOfAYear(ListAPIView):
    permission_classes = [permissions.IsOrganizationStaff]
    pagination_class = None
    serializer_class = PrivateCustomerCountByMonthOfAYearSerializers

    def get_queryset(self):
        kwargs = {"uid": self.kwargs.get("uid", None)}
        year = self.kwargs.get("year", None)
        organization = self.request.user.get_organization()
        customer = get_object_or_404(
            User.objects.filter(
                organizationuser__organization=organization,
                organizationuser__role=OrganizationUserRole.CUSTOMER,
            ),
            **kwargs
        )
        orders = []
        months = {
            1: "january",
            2: "february",
            3: "march",
            4: "april",
            5: "may",
            6: "june",
            7: "july",
            8: "august",
            9: "september",
            10: "october",
            11: "november",
            12: "december",
        }
        for i in range(1, 13):
            months_orders = Order.objects.filter(
                organization=organization,
                customer=customer,
                created_at__year=year,
                created_at__month=i,
            )
            total_order_price = months_orders.aggregate(total_price=Sum("total_price"))[
                "total_price"
            ]
            orders.append(
                {
                    "month": months[i],
                    "count": months_orders.count(),
                    "total_order_price": total_order_price
                    if total_order_price != None
                    else 0,
                }
            )
        return orders


@extend_schema(
    description="Order count by all current status of merchant customer.",
)
class PrivateCustomerOrderCount(RetrieveAPIView):
    serializer_class = OrderCountByStatusSerializer
    permission_classes = [permissions.IsOrganizationStaff]

    def get_object(self):
        kwargs = {"uid": self.kwargs.get("uid", None)}
        organization = self.request.user.get_organization()
        customer = get_object_or_404(
            User.objects.filter(
                organizationuser__organization=organization,
                organizationuser__role=OrganizationUserRole.CUSTOMER,
            ),
            **kwargs
        )

        queryset = Order.objects.filter(
            organization=organization,
            customer=customer,
        )

        lifetime_order_price = queryset.aggregate(
            lifetime_order_price=Sum("total_price")
        )["lifetime_order_price"]

        last_order_date = queryset.filter().order_by("id").latest("id").created_at

        order_count_by_status = []

        orders = queryset.filter(delivery_statuses__stage="CURRENT")

        for key, value in OrderDeliveryStatus.choices:
            order_count = orders.filter(delivery_statuses__status=key).aggregate(
                total_orders=Count("uid")
            )["total_orders"]
            data = {
                "status": key,
                "total_order_count": order_count,
            }
            order_count_by_status.append(data)

        final_data = {
            "order_count_by_status": order_count_by_status,
            "lifetime_order_price": lifetime_order_price,
            "last_order_date": last_order_date.date(),
        }

        return final_data


@extend_schema(
    parameters=[
        OpenApiParameter(
            "search",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="Search by transaction or order serial number",
        ),
        OpenApiParameter(
            "date",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="We can filter transaction by date",
        ),
    ],
    responses=PrivateCustomerTransactionHistoryDetailSerializer,
)
class PrivateCustomerTransactionHistory(RetrieveAPIView):
    serializer_class = PrivateCustomerTransactionHistoryDetailSerializer
    permission_classes = [permissions.IsOrganizationCustomer]

    def get_object(self):
        organization = get_subdomain(self.request)
        previous_due = 0

        transactions: QuerySet[TransactionOrganizationUser] = (
            TransactionOrganizationUser.objects.prefetch_related(
                "order__order_products"
            )
            .filter(user=self.request.user, organization=organization)
            .order_by("created_at")
        )

        for transaction in transactions:
            transaction.previous_due = previous_due
            transaction.current_due = previous_due + (
                transaction.payable_money - transaction.total_money
            )
            previous_due = transaction.current_due

        # searching
        search = self.request.query_params.get("search", "")
        if len(search) > 0:
            transaction_query = transactions.filter(serial_number__icontains=search)
            transaction_order_query = transactions.filter(
                order__serial_number__icontains=search
            )
            transactions = transaction_query | transaction_order_query

        # filtering
        date = self.request.query_params.get("date", "")
        if len(date) > 0:
            transactions = transactions.filter(created_at__date=date)

        transaction_total = transactions.aggregate(
            total_pay=Sum("payable_money", distinct=True, default=0),
            total_money=Sum("order__total_price", distinct=True, default=0),
        )
        make_serializer = {
            "total_pay": transaction_total["total_pay"],
            "total_money": transaction_total["total_money"],
            "balance": transaction_total["total_pay"]
            - transaction_total["total_money"],
            "transactions": transactions,
        }
        return make_serializer
