from rest_framework import serializers
from rest_framework.exceptions import NotFound

from accountio.choices import OrganizationUserRole
from accountio.models import Organization, OrganizationUser, TransactionOrganizationUser
from accountio.utils import get_subdomain

from core.models import User

from orderio.models import OrderDelivery, Order

from weapi.rest.serializers.orders import PrivateOrderDetailSerializer


class PublicNotificationUserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("uid", "first_name", "last_name", "phone", "role")
        read_only_fields = ("__all__",)

    def get_role(self, data: User):
        organization: Organization = get_subdomain(request=self.context["request"])
        try:
            organization_user = OrganizationUser.objects.get(
                organization=organization, user=data
            )
        except OrganizationUser.DoesNotExist:
            raise NotFound(detail="User cannot found in the organization.")

        return (
            "CUSTOMER"
            if organization_user.role == OrganizationUserRole.CUSTOMER
            else "MERCHANT"
        )


class PublicNotificationOrderSerializer(serializers.ModelSerializer):
    customer = PublicNotificationUserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ("uid", "total_price", "serial_number", "created_at", "customer")
        read_only_fields = fields


class PublicNotificationTransactionSerializer(serializers.ModelSerializer):
    user = PublicNotificationUserSerializer(read_only=True)
    order = PrivateOrderDetailSerializer(read_only=True)

    class Meta:
        model = TransactionOrganizationUser
        fields = (
            "uid",
            "serial_number",
            "user",
            "order",
            "total_money",
            "payable_money",
            "note",
        )
        read_only_fields = fields


class PublicNotificationOrderDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDelivery
        fields = ("uid", "status", "stage", "created_at")
        read_only_fields = fields


class PublicNotificationCountSerializer(serializers.Serializer):
    read_count = serializers.IntegerField(min_value=0, read_only=True)
    unread_count = serializers.IntegerField(min_value=0, read_only=True)
