import decimal
import logging
from datetime import datetime
from typing import List

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import (
    transaction,
    IntegrityError,
)

from phonenumber_field.serializerfields import PhoneNumberField

from rest_framework import serializers
from rest_framework.exceptions import ValidationError, APIException

from versatileimagefield.serializers import VersatileImageFieldSerializer

from accountio.choices import OrganizationUserRole
from accountio.models import OrganizationUser, Organization, TransactionOrganizationUser
from accountio.utils import get_subdomain

from addressio.models import Address

from catalogio.models import (
    DeliveryCharge,
    Product,
)
from notificationio.choices import ActivityActionTypeStatusChoices
from notificationio.models import Notification
from notificationio.services import NotificationService
from notificationio.utils import changed_fields_with_values

from orderio.choices import OrderDeliveryStatus, OrderStageChoices
from orderio.models import (
    Order,
    OrderProduct,
    Cart,
    OrderDelivery,
    ReturnOrderProduct,
)

from paymentio.models import PaymentMethod

logger = logging.getLogger(__name__)
User = get_user_model()


class PrivateAddressesSerializer(serializers.ModelSerializer):
    district = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Address
        fields = (
            "uid",
            "label",
            "house_street",
            "upazila",
            "district",
            "division",
            "country",
        )
        read_only_fields = ("__all__",)


class PrivateUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="get_name")
    discount_offset = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "uid",
            "name",
            "phone",
            "discount_offset",
        )
        read_only_fields = ("__all__",)

    def get_discount_offset(self, data):
        organization: Organization = get_subdomain(self.context["request"])
        return OrganizationUser.objects.get(
            organization=organization, user=data
        ).discount_offset


class PrivateOrderDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDelivery
        fields = ("status", "created_at")


class PrivateDeliveryStatusSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = OrderDelivery
        fields = ("status", "stage", "created_at")

    def get_created_at(self, instance: OrderDelivery) -> datetime:
        if (
            instance.status == OrderDeliveryStatus.COMPLETED
            and instance.stage == OrderStageChoices.CURRENT
        ):
            return instance.updated_at
        return instance.updated_at if instance.stage.lower() == "completed" else ""


class MerchantOrderCreateUserSerializer(serializers.Serializer):
    uid = serializers.SlugRelatedField(
        slug_field="uid", queryset=Product.objects.get_status_editable()
    )
    quantity = serializers.IntegerField(min_value=1)


class PrivateOrderListSerializers(serializers.ModelSerializer):
    total_products = serializers.IntegerField(read_only=True)
    customer = PrivateUserSerializer(read_only=True)
    payment_method = serializers.StringRelatedField(read_only=True)
    payable_amount = serializers.DecimalField(
        default=0, decimal_places=2, max_digits=10
    )
    discount = serializers.DecimalField(default=0, decimal_places=2, max_digits=10)
    delivery_statuses = PrivateDeliveryStatusSerializer(read_only=True, many=True)
    # write only fields
    products = MerchantOrderCreateUserSerializer(many=True, write_only=True)
    logged_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    customer_phone = PhoneNumberField(write_only=True)
    first_name = serializers.CharField(
        max_length=255, write_only=True, required=False, allow_blank=True
    )
    last_name = serializers.CharField(
        max_length=255, write_only=True, required=False, allow_blank=True
    )
    payment_method_uid = serializers.SlugRelatedField(
        queryset=PaymentMethod.objects.filter(), slug_field="uid", write_only=True
    )
    returned_total_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = (
            "uid",
            "serial_number",
            "total_products",
            "address",
            "created_at",
            "total_price",
            "delivery_statuses",
            "customer",
            "delivery_charge",
            "receiver_name",
            "receiver_phone",
            "payment_method",
            "payable_amount",
            "returned_total_quantity",
            # write only fields
            "products",
            "customer_phone",
            "first_name",
            "last_name",
            "logged_user",
            "payment_method_uid",
            "discount",
        )
        read_only_fields = (
            "uid",
            "serial_number",
            "total_products",
            "created_at",
            "total_price",
            "delivery_statuses",
            "customer",
            "delivery_charge",
            "receiver_name",
            "receiver_phone",
            "returned_total_quantity",
        )

    def validate_products(self, values: List[MerchantOrderCreateUserSerializer]):
        organization = self.context["request"].user.get_organization()
        stock_none_product_name: List[str] = []

        for i in values:
            product: Product = i["uid"]
            if product.organization != organization:
                raise ValidationError(
                    f"{i['uid'].base_product.name} is a invalid product of {organization.name}"
                )

            if product.stock < i["quantity"]:
                stock_none_product_name.append(product.base_product.name)

        if len(stock_none_product_name) > 0:
            raise ValidationError(
                f"Stock out {'products are: ' if len(stock_none_product_name) > 1 else 'product is: '} {', '.join(stock_none_product_name)}"
            )

        return values

    def create(self, validated_data):
        customer_phone = validated_data.pop("customer_phone")
        first_name = validated_data.pop("first_name", " ")
        last_name = validated_data.pop("last_name", " ")
        address = validated_data.pop("address")
        logged_user = validated_data.pop("logged_user")
        payment_method = validated_data.pop("payment_method_uid")

        organization: Organization = logged_user.get_organization()
        products: List[MerchantOrderCreateUserSerializer] = validated_data.pop(
            "products"
        )
        total_discounted_price = 0
        total_price = 0

        customer, created = User.objects.get_or_create(
            phone=customer_phone,
            defaults={"first_name": first_name, "last_name": last_name},
        )

        organization_user, _ = OrganizationUser.objects.get_or_create(
            organization=organization,
            user=customer,
            defaults={"role": OrganizationUserRole.CUSTOMER},
        )

        offset_price = organization_user.discount_offset
        for order_product in products:
            product: Product = order_product["uid"]
            total_discount = offset_price + product.discount_price
            total_price += product.selling_price * order_product["quantity"]
            single_discounted_price = product.selling_price * (
                1 - (total_discount / decimal.Decimal(100))
            )
            total_discounted_price += (
                single_discounted_price * order_product["quantity"]
            )

            order_product.single_discounted_price = single_discounted_price

        discount = validated_data.get(
            "discount",
            ((total_price - total_discounted_price) / total_price)
            / decimal.Decimal(100),
        )

        payable_amount = validated_data.pop("payable_amount", total_discounted_price)
        order = Order.objects.create(
            customer=customer,
            order_by=logged_user,
            organization=organization,
            order_price=total_discounted_price,
            total_price=total_discounted_price,
            payable_amount=payable_amount,
            address=address,
            delivery_charge=0,
            payment_method=payment_method,
            completed=True,
            discount=discount,
            discount_offset=organization_user.discount_offset,
        )
        for order_product in products:
            product: Product = order_product["uid"]

            OrderProduct.objects.create(
                order=order,
                product=product,
                selling_price=product.selling_price,
                discount_price=product.discount_price + offset_price,
                quantity=order_product["quantity"],
                updated_quantity=order_product["quantity"],
                delivery_quantity=order_product["quantity"],
            )
            product.stock -= order_product["quantity"]
            product.save_dirty_fields()

        # adding delivery status
        for key, value in OrderDeliveryStatus.choices:
            if (
                key != OrderDeliveryStatus.RETURNED
                and key != OrderDeliveryStatus.CANCELED
                and key != OrderDeliveryStatus.PARTIAL_DELIVERY
            ):
                if key == "COMPLETED":
                    OrderDelivery.objects.create(
                        status=key,
                        stage=OrderStageChoices.CURRENT,
                        order=order,
                    )
                else:
                    OrderDelivery.objects.create(
                        status=key,
                        stage=OrderStageChoices.COMPLETED,
                        order=order,
                    )

        transaction_organization_user = TransactionOrganizationUser.objects.create(
            organization=order.organization,
            user=order.customer,
            total_money=order.total_price,
            payable_money=order.payable_amount,
            order=order,
        )

        # sending notification for order
        notification_service = NotificationService(
            request=self.context["request"],
            organization=organization,
        )
        notification: Notification = notification_service.create_notification_with_sending_notification_to_organization_users(
            previous_data={},
            saved_or_updated_instance=order,
        )
        notification_service.send_notification_to_custom_users(
            notification=notification, user_ids=[order.customer.id]
        )

        # sending notification for transaction
        notification_service = NotificationService(
            request=self.context["request"],
            organization=organization,
        )
        notification_service.create_notification_with_sending_notification_to_organization_users(
            previous_data={},
            saved_or_updated_instance=transaction_organization_user,
        )

        return order


class PrivateOrderProductMiniListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="base_product.name")
    unit = serializers.CharField(source="base_product.unit")
    strength = serializers.CharField(source="base_product.strength")
    primary_image = VersatileImageFieldSerializer(
        sizes=[
            ("original", "url"),
            ("at256", "crop__256x256"),
            ("at512", "crop__512x512"),
        ],
        allow_null=True,
        allow_empty_file=True,
        required=False,
        read_only=True,
    )
    manufacturer = serializers.StringRelatedField(source="base_product.manufacturer")
    dosage_form = serializers.CharField(source="base_product.dosage_form")
    active_ingredients = serializers.StringRelatedField(
        source="base_product.active_ingredients", many=True
    )

    class Meta:
        model = Product
        fields = (
            "uid",
            "name",
            "unit",
            "strength",
            "primary_image",
            "manufacturer",
            "dosage_form",
            "active_ingredients",
            "selling_price",
            "discount_price",
            "final_price",
            "box_type",
        )
        read_only_fields = ("__all__",)


class PrivateOrderProductsSerializer(serializers.ModelSerializer):
    product = PrivateOrderProductMiniListSerializer(read_only=True)
    final_price_with_offset = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )

    class Meta:
        model = OrderProduct
        fields = (
            "uid",
            "product",
            "selling_price",
            "quantity",
            "discount_price",
            "updated_quantity",
            "final_price_with_offset",
        )


class PrivateOrderReturnDetailSerializer(serializers.ModelSerializer):
    product = PrivateOrderProductMiniListSerializer()
    quantity = serializers.IntegerField(min_value=0, source="order_product.quantity")
    updated_quantity = serializers.IntegerField(
        min_value=0, source="order_product.updated_quantity"
    )
    final_price_with_offset = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    total_quantity_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = ReturnOrderProduct
        fields = (
            "uid",
            "quantity",
            "returned_quantity",
            "updated_quantity",
            "note",
            "description",
            "is_damage",
            "is_return_by_merchant",
            "product",
            "final_price_with_offset",
            "total_quantity_price",
        )
        read_only_fields = ("__all__",)


class PrivateOrderDetailSerializer(serializers.ModelSerializer):
    order_products = PrivateOrderProductsSerializer(read_only=True, many=True)
    created_at = serializers.DateTimeField(read_only=True)
    address = serializers.JSONField(read_only=True)
    delivery_status_name = serializers.ChoiceField(
        choices=OrderDeliveryStatus.choices, write_only=True
    )
    delivery_statuses = PrivateDeliveryStatusSerializer(read_only=True, many=True)
    payable_amount = serializers.DecimalField(
        default=0, max_digits=10, decimal_places=2
    )
    payment_method = serializers.StringRelatedField()
    customer = PrivateUserSerializer(read_only=True)
    partial_return_products = PrivateOrderReturnDetailSerializer(
        many=True,
        read_only=True,
    )
    partial_delivery_products = PrivateOrderReturnDetailSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = (
            "uid",
            "serial_number",
            "customer",
            "order_products",
            "delivery_charge",
            "total_price",
            "address",
            "created_at",
            "delivery_statuses",
            "delivery_status_name",
            "receiver_name",
            "receiver_phone",
            "payment_method",
            "delivery_charge",
            "payable_amount",
            "partial_return_products",
            "partial_delivery_products",
        )
        read_only_fields = (
            "uid",
            "serial_number",
            "receiver_name",
            "receiver_phone",
            "payment_method",
            "total_price",
        )

    def validate_payable_amount(self, value):
        user_role = self.context["request"].user.get_my_organization_role().lower()
        if user_role not in ["admin", "owner"]:
            raise ValidationError("You do not have permission to change payable amount")
        return value

    def update(self, instance: Order, validated_data):
        # check the delivery charge changed by merchant or not
        if "delivery_charge" in validated_data:
            # if changed, updated the total_price of that order
            validated_data["total_price"] = instance.calculate_updated_price(
                delivery_charge=validated_data.get("delivery_charge")
            )

        instance: Order = super().update(
            instance=instance, validated_data=validated_data
        )

        delivery_name = validated_data.get("delivery_status_name", "")

        try:
            current_delivery_status: str = instance.delivery_statuses.get(
                stage=OrderStageChoices.CURRENT
            ).status
        except OrderDelivery.MultipleObjectsReturned:
            logger.warning("Multiple objects return for order_delivery")
            raise ValidationError({"detail": "Multiple objects have returned."})
        except OrderDelivery.DoesNotExist:
            raise ValidationError(
                {"detail": f"Cannot found the order-delivery current stage."}
            )

        if len(delivery_name) > 0:
            up_to_status = OrderDeliveryStatus.choices.index(
                (delivery_name, dict(OrderDeliveryStatus.choices)[delivery_name])
            )
            current_delivery_index = OrderDeliveryStatus.choices.index(
                (
                    current_delivery_status,
                    dict(OrderDeliveryStatus.choices)[current_delivery_status],
                )
            )
            user_role = self.context["request"].user.get_my_organization_role().lower()

            if user_role not in ["admin", "owner"]:
                if current_delivery_index > up_to_status:
                    raise ValidationError(
                        {
                            "delivery_status_name": [
                                "You do not have permission to back to previous state"
                            ]
                        }
                    )
            # order delivery previous name
            previous_delivery_status: OrderDelivery = instance.delivery_statuses.get(
                stage=OrderStageChoices.CURRENT
            )

            # create the order delivery new status if in DB not available
            order_delivery_current: OrderDelivery = instance.delivery_statuses.get(
                status=delivery_name
            )
            order_delivery_current.stage = OrderStageChoices.CURRENT
            order_delivery_current.save()

            # send notification

            if current_delivery_status != delivery_name:
                notification_service = NotificationService(
                    request=self.context["request"],
                    organization=self.context["request"].user.get_organization(),
                )
                notification: Notification = notification_service.create_notification_with_sending_notification_to_organization_users(
                    previous_data=changed_fields_with_values(
                        "status",
                        previous_delivery_status.status,
                        order_delivery_current.status,
                    ),
                    saved_or_updated_instance=order_delivery_current,
                )
                notification.notificationmodelconnector.order = instance
                notification.notificationmodelconnector.save_dirty_fields()

                notification_service.send_notification_to_custom_users(
                    notification=notification, user_ids=[instance.customer.id]
                )

        # updating the related fields
        try:
            current_set_status = instance.delivery_statuses.get(
                stage=OrderStageChoices.CURRENT
            )
        except OrderDelivery.DoesNotExist:
            raise ValidationError(
                {"detail": f"Cannot found the {delivery_name} status for this order."}
            )

        if current_set_status.status == OrderDeliveryStatus.COMPLETED:
            instance.completed = True
            instance.save_dirty_fields()
            # Added to transaction when the order is completed

            transaction_user = TransactionOrganizationUser.objects.create(
                organization=instance.organization,
                user=instance.customer,
                total_money=instance.total_price,
                payable_money=instance.payable_amount,
                order=instance,
            )
            # sending notification after creating a transaction
            notification_service = NotificationService(
                request=self.context["request"],
                organization=instance.organization,
            )
            notification: Notification = notification_service.create_notification_with_sending_notification_to_organization_users(
                previous_data={},
                saved_or_updated_instance=transaction_user,
                action_type=ActivityActionTypeStatusChoices.ADDITION,
            )
            notification_service.send_notification_to_custom_users(
                notification=notification, user_ids=[transaction_user.user.id]
            )
        else:
            if instance.completed:
                instance.completed = False
                instance.save_dirty_fields()

            TransactionOrganizationUser.objects.filter(
                organization=instance.organization,
                order=instance,
            ).delete()

        return instance


class PrivateProductSerializer(serializers.Serializer):
    slug = serializers.SlugField(read_only=True)
    name = serializers.CharField(label="Product name", read_only=True)
    selling_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, default=0, read_only=True
    )


class PrivateOrderSerializer(serializers.Serializer):
    product = PrivateProductSerializer(read_only=True)
    quantity = serializers.IntegerField(validators=[MinValueValidator(1)])


class PrivateOrderProductMinSerializer(serializers.ModelSerializer):
    active_ingredients = serializers.SerializerMethodField()
    dosage_form = serializers.CharField(source="base_product.dosage_form")
    medicine_physical_state = serializers.CharField(
        source="base_product.medicine_physical_state"
    )
    unit = serializers.CharField(source="base_product.unit")
    strength = serializers.CharField(source="base_product.strength")

    class Meta:
        model = Product
        fields = (
            "name",
            "slug",
            "active_ingredients",
            "unit",
            "strength",
            "dosage_form",
            "medicine_physical_state",
        )

    def get_active_ingredients(self, instance) -> list[str]:
        return [
            dosage_form.name
            for dosage_form in instance.base_product.active_ingredients.all()
        ]


class PrivateOrderProductSerializer(serializers.Serializer):
    selling_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField(validators=[MinValueValidator(1)])
    updated_quantity = serializers.IntegerField(read_only=True)
    active_ingredients = serializers.SerializerMethodField()
    name = serializers.CharField(source="product.base_product.name")
    slug = serializers.CharField(source="product.slug")
    unit = serializers.CharField(source="product.base_product.unit")
    discount_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_quantity_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    strength = serializers.CharField(source="product.base_product.strength")
    dosage_form = serializers.CharField(source="product.base_product.dosage_form")
    box_type = serializers.CharField(source="product.box_type")
    final_price_with_offset = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )

    primary_image = VersatileImageFieldSerializer(
        sizes=[
            ("original", "url"),
            ("at256", "crop__256x256"),
            ("at512", "crop__512x512"),
        ],
        source="product.primary_image",
        allow_null=True,
        allow_empty_file=True,
        required=False,
    )
    medicine_physical_state = serializers.CharField(
        source="product.base_product.medicine_physical_state"
    )
    manufacturer = serializers.StringRelatedField(
        read_only=True, source="product.base_product.manufacturer"
    )

    def get_active_ingredients(self, instance: OrderProduct) -> List[str]:
        return [
            dosage_form.name
            for dosage_form in instance.product.base_product.active_ingredients.all()
        ]


class PrivateReturnOrderProductSerializer(serializers.Serializer):
    uid = serializers.UUIDField(source="order_product.product.uid")
    name = serializers.CharField(source="order_product.product.base_product.name")
    returned_quantity = serializers.IntegerField(read_only=True)
    note = serializers.CharField(read_only=True, max_length=255)
    description = serializers.CharField(read_only=True, max_length=255)
    unit = serializers.CharField(
        source="order_product.product.base_product.unit", read_only=True
    )
    manufacturer = serializers.StringRelatedField(
        source="order_product.product.base_product.manufacturer", read_only=True
    )
    dosage_form = serializers.CharField(
        source="order_product.product.base_product.dosage_form", read_only=True
    )
    selling_price = serializers.DecimalField(
        source="order_product.product.selling_price",
        read_only=True,
        max_digits=10,
        decimal_places=2,
    )
    quantity = serializers.IntegerField(source="order_product.quantity", read_only=True)
    updated_quantity = serializers.IntegerField(
        source="order_product.updated_quantity", read_only=True
    )
    active_ingredients = serializers.SerializerMethodField()
    slug = serializers.CharField(source="order_product.product.slug")
    discount_price = serializers.CharField(
        source="order_product.discount_price", read_only=True
    )
    strength = serializers.CharField(
        source="order_product.product.base_product.strength"
    )
    box_type = serializers.CharField(source="order_product.product.box_type")
    primary_image = VersatileImageFieldSerializer(
        sizes=[
            ("original", "url"),
            ("at256", "crop__256x256"),
            ("at512", "crop__512x512"),
        ],
        source="order_product.product.primary_image",
        allow_null=True,
        allow_empty_file=True,
        required=False,
    )
    medicine_physical_state = serializers.CharField(
        source="order_product.product.base_product.medicine_physical_state"
    )

    def get_active_ingredients(self, instance: OrderProduct) -> List[str]:
        return [
            dosage_form.name
            for dosage_form in instance.product.base_product.active_ingredients.all()
        ]


class PrivateCustomerOrderSerializer(serializers.ModelSerializer):
    products = PrivateOrderProductSerializer(
        many=True, read_only=True, source="order_products"
    )
    partial_delivery_products = PrivateOrderReturnDetailSerializer(
        many=True,
        read_only=True,
    )
    partial_return_products = PrivateOrderReturnDetailSerializer(
        many=True,
        read_only=True,
    )

    delivery_statuses = PrivateDeliveryStatusSerializer(read_only=True, many=True)

    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    address = serializers.JSONField(read_only=True)
    address_uid = serializers.SlugRelatedField(
        queryset=Address.objects.get_status_editable(),
        slug_field="uid",
        write_only=True,
    )
    total_products = serializers.IntegerField(read_only=True)
    payment_method = serializers.StringRelatedField(source="payment_method.name")
    payment_method_uid = serializers.SlugRelatedField(
        queryset=PaymentMethod.objects.filter(),
        slug_field="uid",
        write_only=True,
    )
    is_order_by_merchant = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "uid",
            "serial_number",
            "total_price",
            "payable_amount",
            "order_price",
            "products",
            "address",
            "address_uid",
            "total_products",
            "delivery_charge",
            "payment_method_uid",
            "receiver_name",
            "receiver_phone",
            "payment_method",
            "is_order_by_merchant",
            "customer",
            "delivery_statuses",
            "created_at",
            "partial_delivery_products",
            "partial_return_products",
        )
        read_only_fields = (
            "total_price",
            "total_products",
            "payable_amount",
            "order_price",
            "products",
            "payment_method",
            "delivery_charge",
            "customer",
            "address",
            "delivery_statuses",
            "serial_number",
            "is_order_by_merchant",
        )

    def get_is_order_by_merchant(self, instance: Order) -> bool:
        return bool(
            instance.order_by.organizationuser_set.filter(
                organization=instance.organization,
                role__in=[
                    OrganizationUserRole.OWNER,
                    OrganizationUserRole.ADMIN,
                    OrganizationUserRole.STAFF,
                ],
            ).exists()
        )

    def create(self, validated_data):
        with transaction.atomic():
            organization = get_subdomain(self.context["request"])
            try:
                customer = validated_data.get("customer")
                organization_user = organization.organizationuser_set.get(user=customer)
                try:
                    cart = Cart.objects.prefetch_related("products__product").get(
                        organization=organization, customer=customer
                    )
                except Cart.DoesNotExist:
                    raise ValidationError("Please add some products to cart first.")
                cart_total = cart.total_price()
                cartproducts = cart.products.all()

                # checking insufficient stock products
                insufficient_stock_products = []
                for cart_product in cartproducts:
                    if cart_product.product.stock < cart_product.quantity:
                        insufficient_stock_products.append(
                            cart_product.product.base_product.name
                        )

                if len(insufficient_stock_products) > 0:
                    products_names = ", ".join(insufficient_stock_products)
                    raise ValidationError(
                        {
                            "detail": f"{products_names} {'products are' if len(insufficient_stock_products) > 1 else 'product is'} stocked out"
                        }
                    )

                try:
                    delivery_charge_set = DeliveryCharge.objects.get(
                        organization=organization,
                        district=validated_data.get("address_uid").district,
                    ).charge
                except DeliveryCharge.DoesNotExist:
                    delivery_charge_set = organization.delivery_charge

                address = validated_data.get("address_uid")
                address_json = {
                    "uid": str(address.uid),
                    "label": address.label if address.label else "",
                    "house_street": address.house_street
                    if address.house_street
                    else "",
                    "upazila": address.upazila.name if address.upazila else "",
                    "district": address.district.name if address.district else "",
                    "division": address.division.name if address.division else "",
                    "country": address.country,
                }
                order = Order.objects.create(
                    customer=validated_data.get("customer"),
                    total_price=cart_total + delivery_charge_set,
                    payable_amount=cart_total + delivery_charge_set,
                    order_price=cart_total + delivery_charge_set,
                    address=address_json,
                    payment_method=validated_data.get("payment_method_uid"),
                    delivery_charge=delivery_charge_set,
                    organization=organization,
                    receiver_name=validated_data.get("receiver_name", ""),
                    receiver_phone=validated_data.get("receiver_phone", ""),
                    order_by=customer,
                    discount_offset=organization_user.discount_offset,
                )
                for cartproduct in cartproducts:
                    print(
                        f"product discount {cartproduct.product.name()} -> {cartproduct.product.discount_price}"
                    )
                    OrderProduct.objects.create(
                        order=order,
                        product=cartproduct.product,
                        selling_price=cartproduct.product.selling_price,
                        discount_price=cartproduct.product.discount_price
                        + organization_user.discount_offset,
                        quantity=cartproduct.quantity,
                        updated_quantity=cartproduct.quantity,
                        delivery_quantity=cartproduct.quantity,
                    )
                    cartproduct.product.stock = (
                        cartproduct.product.stock - cartproduct.quantity
                    )
                    cartproduct.product.save()
                statuses = []
                for key, value in OrderDeliveryStatus.choices:
                    if key == OrderDeliveryStatus.ORDER_PLACED:
                        statuses.append(
                            OrderDelivery(
                                status=key,
                                stage=OrderStageChoices.CURRENT,
                                order=order,
                            )
                        )
                    else:
                        statuses.append(
                            OrderDelivery(
                                status=key,
                                stage=OrderStageChoices.PENDING,
                                order=order,
                            )
                        )

                OrderDelivery.objects.bulk_create(statuses)

                cart.delete()

                # sending notification
                notification_service = NotificationService(
                    request=self.context["request"],
                    organization=organization,
                )
                notification: Notification = notification_service.create_notification_with_sending_notification_to_organization_users(
                    previous_data={},
                    saved_or_updated_instance=order,
                )
                notification_service.send_notification_to_custom_users(
                    notification=notification, user_ids=[order.customer.id]
                )
            except IntegrityError as e:
                raise ValidationError(e)

        return order


class PrivateDeliveryChargeListSerializers(serializers.ModelSerializer):
    class Meta:
        model = DeliveryCharge
        fields = [
            "district",
            "charge",
        ]

    def validate_district(self, value):
        organization = get_subdomain(self.context["request"])
        if DeliveryCharge.objects.filter(
            district=value, organization=organization
        ).exists():
            raise ValidationError("The district already listed", code=422)
        return value

    def create(self, validated_data):
        with transaction.atomic():
            organization = get_subdomain(self.context["request"])
            district = validated_data.get("district")
            charge = validated_data.get("charge")

            return DeliveryCharge.objects.create(
                district=district,
                charge=charge,
                organization=organization,
            )


class PrivateDeliveryChargeSerializers(serializers.Serializer):
    charge = serializers.DecimalField(max_digits=10, decimal_places=2)

    def update(self, instance, validated_data):
        instance.charge = validated_data.get("charge")
        instance.save()
        return instance


class PrivateCustomerCountByMonthOfAYearSerializers(serializers.Serializer):
    month = serializers.CharField(read_only=True)
    count = serializers.IntegerField(read_only=True)
    total_order_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )


class OrderCountSerializer(serializers.Serializer):
    status = serializers.CharField(read_only=True)
    total_order_count = serializers.IntegerField(read_only=True)


class OrderCountByStatusSerializer(serializers.Serializer):
    order_count_by_status = OrderCountSerializer(many=True)
    lifetime_order_price = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )
    last_order_date = serializers.DateField(read_only=True)


class PrivateReturnOrderProductListSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(
        queryset=Product.objects.get_status_editable(),
        slug_field="uid",
        write_only=True,
    )

    class Meta:
        model = ReturnOrderProduct
        fields = [
            "uid",
            "product",
            "returned_quantity",
            "note",
            "description",
            "is_damage",
        ]


class PrivateReturnProductHoldSerializer(serializers.Serializer):
    return_products = PrivateReturnOrderProductListSerializer(
        many=True, write_only=True
    )

    def update(self, instance: Order, validated_data):
        return_products = validated_data.pop("return_products", [])
        delivery_status = instance.delivery_statuses.get(stage="CURRENT").status

        if (
            delivery_status == OrderDeliveryStatus.PARTIAL_RETURNED
            or delivery_status == OrderDeliveryStatus.PARTIAL_DELIVERY
        ):
            for product in return_products:
                order_product = instance.order_products.get(product=product["product"])
                returned_quantity = product["returned_quantity"]
                if returned_quantity == 0:
                    continue
                if order_product.updated_quantity >= product["returned_quantity"]:
                    ReturnOrderProduct.objects.create(
                        order=order_product.order,
                        organization=instance.organization,
                        product=order_product.product,
                        returned_quantity=product["returned_quantity"],
                        note=product["note"],
                        description=product["description"],
                        is_damage=product["is_damage"],
                        order_product=order_product,
                        is_return_by_merchant=True
                        if delivery_status == OrderDeliveryStatus.PARTIAL_DELIVERY
                        else False,
                    )
                else:
                    raise ValidationError(
                        {
                            "returned_quantity": f"Maximum return product {order_product.product.base_product.name} exceed."
                        }
                    )

                # product = Product.objects.get(pk=product["product"].id)
                if product["is_damage"]:
                    product["product"].damage_stock += product["returned_quantity"]
                else:
                    product["product"].stock += product["returned_quantity"]
                product["product"].save_dirty_fields()

                # saved order product
                order_product.updated_quantity -= product["returned_quantity"]
                order_product.save_dirty_fields()

            instance.total_price = instance.calculate_updated_price()
            instance.save_dirty_fields()

        else:
            raise ValidationError(
                {
                    "detail": "Please make your status partially delivered or partially returned"
                }
            )

        return instance
