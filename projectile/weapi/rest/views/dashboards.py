from datetime import datetime, timedelta

from django.db.models import (
    F,
    Sum,
    OuterRef,
    Count,
    IntegerField,
    Subquery,
    DecimalField,
)
from django.db.models.functions import Cast, Coalesce

from rest_framework.generics import RetrieveAPIView

from accountio.choices import OrganizationUserRole
from accountio.models import OrganizationUser, TransactionOrganizationUser

from catalogio.models import Product, Category

from core.models import User

from orderio.choices import OrderDeliveryStatus
from orderio.models import Order

from weapi.rest.permissions import IsOrganizationStaff
from weapi.rest.serializers.dashboards import PrivateDashboardDetailSerializer


class PrivateDashboardList(RetrieveAPIView):
    permission_classes = [IsOrganizationStaff]
    serializer_class = PrivateDashboardDetailSerializer

    def get_object(self):
        starttime = self.request.query_params.get(
            "starttime", datetime.now() - timedelta(days=7)
        )

        organization = self.request.user.get_organization()

        order_status_placed = 0

        # total organization's order count
        total_order_count = Order.objects.filter(organization=organization).count()

        count_by_order_status = dict()
        for i, j in OrderDeliveryStatus.choices:
            order_status_placed = Order.objects.filter(
                organization=organization,
                delivery_statuses__status=i,
                delivery_statuses__stage="CURRENT",
            )
            total_price = order_status_placed.aggregate(
                total_price=Sum("total_price", default=0)
            )["total_price"]

            count_by_order_status[i] = {
                "count": order_status_placed.count(),
                "total_price": total_price if total_price else 0,
            }

        customer_count = OrganizationUser.objects.filter(
            organization=organization,
            role=OrganizationUserRole.CUSTOMER,
            user__created_at__gte=starttime,
        ).count()

        total_stocked_product_sum = Product.objects.filter(
            organization=self.request.user.get_organization(), stock__gt=0
        ).aggregate(total_sum=Sum(F("stock") * F("final_price"), default=0))[
            "total_sum"
        ]

        stock_sum_inventory_products_count = Product.objects.filter(
            organization=organization
        ).aggregate(total_count=Sum("stock", default=0))
        inventory_products_count = Product.objects.filter(
            organization=organization
        ).count()

        inventory_unique_products_count = (
            Product.objects.filter(organization=organization).distinct().count()
        )

        categories_product = (
            Category.objects.filter(
                baseproduct__get_products__organization=organization
            )
            .annotate(total_stock=Sum("baseproduct__get_products__stock"))
            .values(category_name=F("name"), total_stock=F("total_stock"))
        )

        transaction_subquery = (
            TransactionOrganizationUser.objects.filter(
                organization=OuterRef("organization_id"), user=OuterRef("id")
            )
            .values("organization")
            .annotate(total_payable_money=Sum("payable_money", default=0))
            .values("total_payable_money")
        )

        order_subquery = (
            Order.objects.filter(
                organization=OuterRef("organization_id"), customer=OuterRef("id")
            )
            .values("organization")
            .annotate(total_buying_money=Sum("total_price", default=0))
            .values("total_buying_money")
        )

        organization_user_with_balance = (
            User.objects.annotate(
                total_orders=Count("orders"),
                organization=Cast(organization.id, IntegerField()),
                organization_id=F("organizationuser__organization_id"),
                total_payable_money=Subquery(
                    transaction_subquery,
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                ),
                total_buying_money=Subquery(
                    order_subquery,
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                ),
                balance=Coalesce(
                    F("total_payable_money") - F("total_buying_money"),
                    0,
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                ),
            )
            .prefetch_related("organizationuser_set")
            .filter(
                organizationuser__organization=organization,
                organizationuser__role=OrganizationUserRole.CUSTOMER,
            )
            .order_by("-created_at")
        )

        advance = organization_user_with_balance.filter(balance__gt=0)
        due = organization_user_with_balance.filter(balance__lt=0)

        count_customer_with_advance_payment = advance.count()
        count_customer_with_due_amount = due.count()

        return {
            "count_and_total_by_status": count_by_order_status,
            "customer_count": customer_count,
            "product_stock_price_sum": total_stocked_product_sum,
            "product_stock_count_sum": stock_sum_inventory_products_count,
            "inventory_products_count": inventory_products_count,
            "inventory_unique_products_count": inventory_unique_products_count,
            "categories_product": categories_product,
            "advance": advance,
            "due": due,
            "count_customer_with_advance_payment": count_customer_with_advance_payment,
            "count_customer_with_due_amount": count_customer_with_due_amount,
            "total_order_count": total_order_count,
        }
