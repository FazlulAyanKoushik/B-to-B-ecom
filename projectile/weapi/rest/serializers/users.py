from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction

from phonenumber_field.serializerfields import PhoneNumberField

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accountio.choices import OrganizationUserRole
from accountio.models import OrganizationUser, TransactionOrganizationUser, Organization
from accountio.utils import get_subdomain

from core.rest.serializers.auth import GlobalUserSlimSerializer

from notificationio.models import Notification
from notificationio.services import NotificationService

from orderio.models import Order

User = get_user_model()


class PrivateOrganizationUserSerializer(serializers.ModelSerializer):
    user = GlobalUserSlimSerializer(read_only=True)

    class Meta:
        model = OrganizationUser
        fields = [
            "uid",
            "user",
            "discount_offset",
            "role",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uid", "user", "created_at", "updated_at"]

    def update(self, instance, validated_data):
        instance.discount_offset = validated_data.get(
            "discount_offset", instance.discount_offset
        )
        instance.role = validated_data.get("role", instance.role)
        instance.status = validated_data.get("status", instance.status)
        # get the changed data with verbose
        changed_data = instance.get_dirty_fields(verbose=True)

        # save the instance
        instance.save_dirty_fields()

        # sending notification
        organization = get_subdomain(self.context["request"])

        if changed_data:
            notification_service = NotificationService(
                request=self.context["request"],
                organization=organization,
            )
            notification: Notification = notification_service.create_notification_with_sending_notification_to_organization_users(
                previous_data=changed_data,
                saved_or_updated_instance=instance,
            )
            if (
                organization.organizationuser_set.get(user=instance.user).role
                == "CUSTOMER"
            ):
                notification_service.send_notification_to_custom_users(
                    notification=notification, user_ids=[instance.user.id]
                )

        return instance


class PrivateOrganizationPostSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    role = serializers.ChoiceField(
        choices=OrganizationUserRole.choices, write_only=True
    )
    first_name = serializers.CharField(allow_blank=True, write_only=True)
    last_name = serializers.CharField(allow_blank=True, write_only=True)
    email = serializers.EmailField(allow_blank=True, write_only=True)
    phone = PhoneNumberField(write_only=True)
    password = serializers.CharField(max_length=255, write_only=True)

    def create(self, validated_data):
        with transaction.atomic():
            organization = validated_data.get("user").get_organization()
            phone = validated_data.get("phone")
            user, _ = User.objects.get_or_create(
                phone=phone,
                defaults={
                    "first_name": validated_data.get("first_name", None),
                    "last_name": validated_data.get("last_name", None),
                    "phone": phone,
                    "password": make_password(validated_data.get("password")),
                    "email": validated_data.get("email"),
                },
            )
            role = validated_data.get("role")
            organization_set = OrganizationUser.objects.filter(
                organization=organization, user=user
            )
            if organization_set.exists():
                raise ValidationError(
                    {
                        "detail": "This user is already added to your current organization."
                    }
                )
            else:
                organization_set = OrganizationUser.objects.create(
                    organization=organization, user=user, role=role, is_default=True
                )

        return organization_set


class OrderSerializer(serializers.ModelSerializer):
    total_products = serializers.SerializerMethodField()

    class Meta:
        model = Order

        fields = ["serial_number", "total_price", "payable_amount", "total_products"]

        read_only_fields = ("__all__",)

    def get_total_products(self, obj):
        return obj.order_products.count()


class PrivateCustomerTransactionListSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2,
        read_only=True,
        source="total_amount",
    )
    order = OrderSerializer()

    class Meta:
        model = TransactionOrganizationUser
        fields = [
            "serial_number",
            "amount",
            "order",
        ]
        read_only_fields = ("__all__",)


class OrderCountSerializer(serializers.Serializer):
    status = serializers.CharField(read_only=True)
    total_order_count = serializers.IntegerField(read_only=True)


class OrderCountByStatusSerializer(serializers.Serializer):
    order_count_by_status = OrderCountSerializer(many=True)
    lifetime_order_price = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2, default=0
    )
    lifetime_paid_amount = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2, default=0
    )

    last_order_date = serializers.DateField(read_only=True)


class PrivateCustomerCountByMonthOfAYearSerializers(serializers.Serializer):
    month = serializers.CharField(read_only=True)
    count = serializers.IntegerField(read_only=True)
    total_order_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
