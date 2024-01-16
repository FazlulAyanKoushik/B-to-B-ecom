from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum, QuerySet, Count

from drf_spectacular.utils import extend_schema

from rest_framework import filters
from rest_framework.exceptions import ValidationError, APIException, NotFound
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    get_object_or_404,
    RetrieveAPIView,
    CreateAPIView,
    ListAPIView,
)

from accountio.choices import OrganizationUserRole
from accountio.models import OrganizationUser, TransactionOrganizationUser, Organization

from notificationio.models import Notification
from notificationio.services import NotificationService

from orderio.choices import OrderDeliveryStatus
from orderio.models import Order

from weapi.rest import permissions
from weapi.rest.serializers.organizations import (
    PrivateCustomerTransactionHistoryDetailSerializer,
)
from weapi.rest.serializers.users import (
    PrivateOrganizationUserSerializer,
    PrivateOrganizationPostSerializer,
    OrderCountByStatusSerializer,
    PrivateCustomerCountByMonthOfAYearSerializers,
)

User = get_user_model()


@extend_schema(
    description="The organization-user list can be viewed by admin, owner, manager, and staff. Only admin, owner, and manager have permission to create organization-user."
)
class PrivateOrganizationUserList(ListCreateAPIView):
    queryset = OrganizationUser.objects.get_status_editable()

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsOrganizationManager()]
        else:
            return [permissions.IsOrganizationStaff()]

    filter_backends = [filters.SearchFilter]
    search_fields = [
        "^user__first_name",
        "^user__last_name",
        "user__phone",
        "user__email",
    ]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return PrivateOrganizationUserSerializer
        else:
            return PrivateOrganizationPostSerializer

    def get_queryset(self):
        organization: Organization = self.request.user.get_organization()
        organization_user: QuerySet[OrganizationUser] = (
            self.queryset.filter(organization=organization)
            .select_related("user", "organization")
            .order_by("-role")
        )
        return organization_user

    def perform_create(self, serializer):
        role = serializer.validated_data.get("role", None)
        if (
            role
            and role == "owner"
            and serializer.validated_data.get("user").get_my_organization_role().lower()
            != "owner"
        ):
            raise ValidationError("Unauthorized access", code=422)
        if (
            role
            and (role == "admin" or role == "staff")
            and serializer.validated_data.get("user").get_my_organization_role().lower()
            == "staff"
        ):
            raise ValidationError("Unauthorized access", code=422)

        with transaction.atomic():
            instance: OrganizationUser = serializer.save()

            # sending notification
            notification_service = NotificationService(
                request=self.request,
            )
            notification: Notification = notification_service.create_notification_with_sending_notification_to_organization_users(
                previous_data={},
                saved_or_updated_instance=instance,
            )
            if role == "CUSTOMER":
                notification_service.send_notification_to_custom_users(
                    notification=notification, user_ids=[instance.user.id]
                )

            return serializer


@extend_schema(
    description="The organization-user can be viewed by admin, owner, manager, and staff. Only admin or owner have permission to update or removed organization-user."
)
class PrivateOrganizationUserDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = PrivateOrganizationUserSerializer

    queryset = OrganizationUser.objects.select_related(
        "user", "organization"
    ).get_status_editable()

    def get_object(self):
        user_uid = self.kwargs.get("user_uid", None)
        organization = self.request.user.get_organization()

        return get_object_or_404(
            self.queryset.filter(organization=organization),
            user__uid=user_uid,
        )

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsOrganizationAdmin()]

        return [permissions.IsOrganizationStaff()]


@extend_schema(
    description="The transaction can be viewed by admin, owner, manager, and staff. Only admin, owner, and manager have permission to create transaction."
)
class PrivateCustomerTransactionHistoryList(CreateAPIView, RetrieveAPIView):
    serializer_class = PrivateCustomerTransactionHistoryDetailSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsOrganizationManager()]

        return [permissions.IsOrganizationStaff()]

    def get_object(self):
        organization = self.request.user.get_organization()
        try:
            user: User = User.objects.prefetch_related(
                "transactionorganizationuser_set__organization",
                "transactionorganizationuser_set__order",
                "organizationuser_set",
            ).get(uid=self.kwargs.get("uid"))

        except User.DoesNotExist:
            raise NotFound(detail="User cannot found.")

        previous_due = 0
        date = self.request.query_params.get("date", "")
        transactions: QuerySet[
            TransactionOrganizationUser
        ] = user.transactionorganizationuser_set.filter(organization=organization)

        for transaction in transactions:
            transaction.previous_due = previous_due
            transaction.current_due = previous_due + (
                transaction.payable_money - transaction.total_money
            )
            previous_due = transaction.current_due

        if len(date) > 0:
            transactions = transactions.filter(created_at__date=date)

        transaction_total_pay = transactions.aggregate(
            total_pay=Sum("payable_money", default=0),
        ).get("total_pay", 0)

        order_total_money = user.orders
        if len(date) > 0:
            order_total_money = order_total_money.filter(created_at__date=date)
        order_total_money = order_total_money.aggregate(
            order_total_price=Sum("total_price", default=0)
        ).get("order_total_price", 0)

        make_serializer = {
            "total_pay": transaction_total_pay,
            "total_money": order_total_money,
            "transactions": transactions,
        }

        return make_serializer

    def perform_create(self, serializer):
        uid = self.kwargs.get("uid", None)
        organization = self.request.user.get_organization()
        total_money = 0
        user = User.objects.get(uid=uid)
        with transaction.atomic():
            transaction_user = TransactionOrganizationUser.objects.create(
                user=user,
                organization=organization,
                total_money=total_money,
                note=serializer.validated_data.get("note", ""),
                payable_money=serializer.validated_data.get("payable_money"),
            )
            # sending notification
            notification_service = NotificationService(
                request=self.request,
                organization=organization,
            )
            notification: Notification = notification_service.create_notification_with_sending_notification_to_organization_users(
                previous_data={},
                saved_or_updated_instance=transaction_user,
            )
            notification_service.send_notification_to_custom_users(
                notification=notification, user_ids=[transaction_user.user.id]
            )


class PrivateCustomerCountByMonthOfAYear(ListAPIView):
    permission_classes = [permissions.IsOrganizationStaff]
    pagination_class = None
    serializer_class = PrivateCustomerCountByMonthOfAYearSerializers

    def get_queryset(self):
        kwargs = {"uid": self.kwargs.get("customer_uid", None)}
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
        kwargs = {"uid": self.kwargs.get("customer_uid", None)}
        organization = self.request.user.get_organization()
        customer = get_object_or_404(
            User.objects.filter(
                organizationuser__organization=organization,
                organizationuser__role=OrganizationUserRole.CUSTOMER,
            ),
            **kwargs
        )
        try:
            queryset = Order.objects.filter(
                organization=organization,
                customer=customer,
            )
            # lifetime paid amount
            lifetime_paid_amount = TransactionOrganizationUser.objects.filter(
                organization=organization, user=customer
            ).aggregate(total_pay=Sum("payable_money", default=0))["total_pay"]

            lifetime_order_price = queryset.aggregate(
                lifetime_order_price=Sum("total_price", default=0)
            )["lifetime_order_price"]

            last_order_date = queryset.filter().order_by("id").latest("id").created_at
        except Order.DoesNotExist:
            raise APIException(detail="Invalid order.")

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
            "lifetime_paid_amount": lifetime_paid_amount,
            "last_order_date": last_order_date.date(),
        }

        return final_data
