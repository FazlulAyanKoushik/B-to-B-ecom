from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from versatileimagefield.serializers import VersatileImageFieldSerializer

from accountio.choices import OrganizationUserRole, OrganizationUserStatus
from accountio.models import Organization, OrganizationUser, TransactionOrganizationUser

from addressio.models import District, Address

from catalogio.models import Product, Manufacturer, DosageForm
from catalogio.utils import discount_price_calculator

from notificationio.services import NotificationService

from orderio.models import Order

from phonenumber_field.serializerfields import PhoneNumberField

from .addresses import PrivateAddressesListDetailSerializer

User = get_user_model()


class PrivateAddressDistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = [
            "uid",
            "name",
        ]

        read_only_fields = [
            "uid",
            "name",
        ]


class PrivateCustomerSerializer(serializers.ModelSerializer):
    total_orders = serializers.IntegerField(read_only=True)
    discount_offset = serializers.IntegerField(read_only=True, default=0)
    role = serializers.CharField(read_only=True)
    balance = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    addresses = PrivateAddressesListDetailSerializer(
        read_only=True, source="address_set", many=True
    )

    class Meta:
        model = User
        fields = [
            "uid",
            "first_name",
            "last_name",
            "phone",
            "discount_offset",
            "role",
            "balance",
            "total_orders",
            "created_at",
            "addresses",
        ]
        read_only_fields = (
            "uid",
            "first_name",
            "last_name",
            "phone",
            "discount_offset",
            "role",
            "balance",
            "total_orders",
            "created_at",
            "addresses",
        )


class PrivateCustomerDetailSerializer(serializers.ModelSerializer):
    discount_offset = serializers.IntegerField(required=False)
    role = serializers.ChoiceField(choices=OrganizationUserRole.choices, read_only=True)
    total_pay = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )
    total_money = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )
    addresses = PrivateAddressesListDetailSerializer(
        read_only=True, source="address_set", many=True
    )

    class Meta:
        model = User
        fields = [
            "uid",
            "first_name",
            "last_name",
            "phone",
            "email",
            "status",
            "created_at",
            "discount_offset",
            "discount_offset",
            "role",
            "total_pay",
            "total_money",
            "addresses",
        ]
        read_only_fields = (
            "uid",
            "first_name",
            "last_name",
            "phone",
            "email",
            "status",
            "created_at",
            "role",
            "total_pay",
            "total_money",
        )

    def update(self, instance, validated_data):
        discount_offset = validated_data.get("discount_offset", None)
        organization = instance.organization
        if discount_offset is not None:
            organization_user = instance.organizationuser_set.get(
                organization=organization
            )
            organization_user.discount_offset = discount_offset
            organization_user.save_dirty_fields()

            instance.discount_offset = discount_offset

        return instance


class PrivateOrganizationInfoSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    role = serializers.ChoiceField(
        choices=OrganizationUserRole.choices,
        read_only=True,
        source="get_my_organization_role",
    )
    name = serializers.CharField(max_length=255, read_only=True, source="get_name")
    status = serializers.ChoiceField(
        choices=OrganizationUserStatus.choices,
        read_only=True,
        source="get_merchent_organization_user.status",
    )
    phone = PhoneNumberField(read_only=True)
    organization_name = serializers.CharField(max_length=255, read_only=True)
    organization_domain = serializers.CharField(max_length=255, read_only=True)
    organization_uid = serializers.UUIDField(read_only=True)


class PrivateEmployeeSerializers(serializers.Serializer):
    name = serializers.CharField(max_length=100, read_only=True, source="user.get_name")
    role = serializers.CharField(max_length=100, read_only=True)
    phone = PhoneNumberField(read_only=True, source="user.phone")


class PrivateOrganizationDetailSerializer(serializers.ModelSerializer):
    store_front_photo = VersatileImageFieldSerializer(
        allow_null=True,
        allow_empty_file=True,
        required=False,
        sizes=[
            ("original", "url"),
            ("at256", "crop__256x256"),
            ("at512", "crop__512x512"),
        ],
    )
    logo = VersatileImageFieldSerializer(
        allow_null=True,
        allow_empty_file=True,
        required=False,
        sizes=[
            ("original", "url"),
            ("at256", "crop__256x256"),
            ("at512", "crop__512x512"),
        ],
    )

    class Meta:
        model = Organization
        fields = (
            "uid",
            "name",
            "kind",
            "domain",
            "slug",
            "tax_number",
            "registration_no",
            "delivery_charge",
            "contact_number",
            "website_url",
            "blog_url",
            "linkedin_url",
            "instagram_url",
            "facebook_url",
            "twitter_url",
            "whatsapp_number",
            "imo_number",
            "store_front_photo",
            "logo",
            "summary",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "uid",
            "created_at",
            "updated_at",
            "domain",
            "slug",
        )

    def validate_store_front_photo(self, data):
        if data:
            self.instance.store_front_photo.delete_all_created_images()
        return data

    def validate_logo(self, data):
        if data:
            self.instance.logo.delete_all_created_images()
        return data

    def update(self, instance: Organization, validated_data):
        instance.kind = validated_data.get("kind", instance.kind)
        instance.tax_number = validated_data.get("tax_number", instance.tax_number)
        instance.registration_no = validated_data.get(
            "registration_no", instance.registration_no
        )
        instance.delivery_charge = validated_data.get(
            "delivery_charge", instance.delivery_charge
        )
        instance.contact_number = validated_data.get(
            "contact_number", instance.contact_number
        )
        instance.website_url = validated_data.get("website_url", instance.website_url)
        instance.blog_url = validated_data.get("blog_url", instance.blog_url)
        instance.linkedin_url = validated_data.get(
            "linkedin_url", instance.linkedin_url
        )
        instance.instagram_url = validated_data.get(
            "instagram_url", instance.instagram_url
        )
        instance.facebook_url = validated_data.get(
            "facebook_url", instance.facebook_url
        )
        instance.twitter_url = validated_data.get("twitter_url", instance.twitter_url)
        instance.whatsapp_number = validated_data.get(
            "whatsapp_number", instance.whatsapp_number
        )
        instance.imo_number = validated_data.get("imo_number", instance.imo_number)
        instance.store_front_photo = validated_data.get(
            "store_front_photo", instance.store_front_photo
        )
        instance.logo = validated_data.get("logo", instance.logo)
        instance.summary = validated_data.get("summary", instance.summary)
        instance.description = validated_data.get("description", instance.description)

        # get the changed data
        changed_data = instance.get_dirty_fields(verbose=True)

        # save the instance
        instance.save_dirty_fields()

        notification_service = NotificationService(
            request=self.context["request"],
            organization=instance,
        )
        notification_service.create_notification_with_sending_notification_to_organization_users(
            previous_data=changed_data,
            saved_or_updated_instance=instance,
        )
        return instance

    # def to_representation(self, instance):
    #     try:
    #         instance = super().to_representation(instance)
    #     except FileNotFoundError:
    #         instance.store_front_photo.delete_all_created_images()
    #         try:
    #             instance = super().to_representation(instance)
    #         except FileNotFoundError:
    #             instance.logo.delete_all_created_images()
    #             instance = super().to_representation(instance)
    #     return instance


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            "uid",
            "label",
            "house_street",
            "upazila",
            "division",
            "district",
            "country",
            "status",
        )


class PrivateOrganizationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    role = serializers.CharField(read_only=True)
    address = AddressSerializer(source="address_set", many=True, read_only=True)
    store_front_photo = VersatileImageFieldSerializer(
        allow_null=True,
        allow_empty_file=True,
        required=False,
        sizes=[
            ("original", "url"),
            ("at256", "crop__256x256"),
            ("at512", "crop__512x512"),
        ],
    )
    logo = VersatileImageFieldSerializer(
        allow_null=True,
        allow_empty_file=True,
        required=False,
        sizes=[
            ("original", "url"),
            ("at256", "crop__256x256"),
            ("at512", "crop__512x512"),
        ],
    )

    class Meta:
        model = Organization
        fields = (
            "uid",
            "user",
            "name",
            "slug",
            "domain",
            "kind",
            "tax_number",
            "registration_no",
            "delivery_charge",
            "contact_number",
            "website_url",
            "blog_url",
            "linkedin_url",
            "instagram_url",
            "facebook_url",
            "twitter_url",
            "whatsapp_number",
            "imo_number",
            "address",
            "summary",
            "logo",
            "role",
            "description",
            "store_front_photo",
        )
        read_only_fields = ("uid", "domain")

    def create(self, validated_data):
        user = validated_data.pop("user")
        organization = super().create(validated_data=validated_data)
        OrganizationUser.objects.create(
            user=user,
            organization=organization,
            role=OrganizationUserRole.OWNER,
            is_default=True,
        )
        return organization


class PrivateProductBulkDiscountSerializer(serializers.Serializer):
    products = serializers.SlugRelatedField(
        slug_field="uid",
        queryset=Product.objects.order_by(
            "base_product__name" ""
        ).get_status_editable(),
        many=True,
        required=False,
        allow_null=True,
        allow_empty=True,
    )
    manufacturer = serializers.SlugRelatedField(
        queryset=Manufacturer.objects.filter(),
        slug_field="uid",
        allow_null=True,
        allow_empty=True,
        required=False,
    )
    dosage_form = serializers.SlugRelatedField(
        queryset=DosageForm.objects.filter(),
        slug_field="uid",
        allow_null=True,
        allow_empty=True,
        required=False,
    )
    discount_percent = serializers.IntegerField(min_value=0, max_value=100)
    merchant = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate(self, attrs):
        products = attrs.get("products", [])
        manufacturer: Manufacturer = attrs.get("manufacturer", None)
        organization: Organization = self.context["request"].user.get_organization()
        organization_products = organization.product_set.prefetch_related(
            "base_product__manufacturer"
        ).filter()

        if len(products) <= 0 and manufacturer is None:
            raise ValidationError(
                {"detail": "Either manufacturer or products must have value"}
            )
        if len(products) > 0:
            error_product_names = []
            for product in products:
                if not organization_products.filter(pk=product.id).exists():
                    error_product_names.append(product.name().title())
            if error_product_names:
                raise ValidationError(
                    {
                        "products": f"{', '.join(error_product_names)} is not your organization product."
                    }
                )

        if manufacturer is not None:
            if not organization_products.filter(
                base_product__manufacturer=manufacturer
            ).exists():
                raise ValidationError(
                    {
                        "manufacturer": f"{manufacturer.name.title()} is not your listed organization."
                    }
                )

        return attrs

    def create(self, validated_data):
        products = validated_data.get("products", [])
        merchant = validated_data.get("merchant", "")
        current_organization: Organization = merchant.get_organization()
        manufacturer = validated_data.get("manufacturer", "")
        dosage_form = validated_data.get("dosage_form", "")
        discount_percent = validated_data.get("discount_percent", 0)

        if len(products) > 0:
            bulk_products = []
            for product in products:
                bulk_products.append(
                    Product(
                        id=product.id,
                        discount_price=discount_percent,
                        final_price=discount_price_calculator(
                            selling_price=product.selling_price,
                            discount_price=discount_percent,
                        ),
                    )
                )
            Product.objects.bulk_update(
                bulk_products, ["discount_price", "final_price"]
            )

        elif manufacturer:
            products_by_manufacturer = current_organization.product_set.filter(
                base_product__manufacturer=manufacturer
            )
            if dosage_form:
                products_by_manufacturer = products_by_manufacturer.filter(
                    base_product__dosage_form=dosage_form
                )

            products_by_manufacturer.update(discount_price=discount_percent)
            updated_products = []

            for product in products_by_manufacturer:
                updated_products.append(
                    Product(
                        id=product.id,
                        final_price=discount_price_calculator(
                            selling_price=product.selling_price,
                            discount_price=product.discount_price,
                        ),
                    )
                )

            Product.objects.bulk_update(updated_products, ["final_price"])

        else:
            ...
        return validated_data


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["name", "slug"]
        read_only_fields = ("__all__",)


class OrderSerializer(serializers.ModelSerializer):
    total_products = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["serial_number", "total_price", "payable_amount", "total_products"]
        read_only_fields = ("__all__",)

    def get_total_products(self, obj: Order) -> int:
        return obj.order_products.count()


class PrivateCustomerTransactionHistoryListSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()
    previous_due = serializers.DecimalField(decimal_places=2, max_digits=10, default=0)
    current_due = serializers.DecimalField(decimal_places=2, max_digits=10, default=0)
    order = OrderSerializer()

    class Meta:
        model = TransactionOrganizationUser
        fields = [
            "serial_number",
            "organization",
            "order",
            "total_money",
            "note",
            "payable_money",
            "created_at",
            "previous_due",
            "current_due",
        ]
        read_only_fields = ("__all__",)


class PrivateCustomerTransactionHistoryDetailSerializer(serializers.Serializer):
    total_pay = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )
    total_money = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )
    transactions = PrivateCustomerTransactionHistoryListSerializer(
        many=True, read_only=True
    )
    payable_money = serializers.DecimalField(
        write_only=True, max_digits=10, decimal_places=2
    )
    balance = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    note = serializers.CharField(max_length=700, write_only=True, allow_blank=True)
