import decimal
import logging
import re
from decimal import Decimal

from django.core.validators import FileExtensionValidator
from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

import pandas as pd

from versatileimagefield.serializers import VersatileImageFieldSerializer

from accountio.models import Organization

from catalogio.choices import ProductBoxType

from catalogio.models import (
    BaseProduct,
    Brand,
    Category,
    DosageForm,
    Ingredient,
    Manufacturer,
    MedicinePhysicalState,
    Product,
    RouteOfAdministration,
)

from mediaroomio.choices import MediaImageConnectorKind
from mediaroomio.models import MediaImageConnector, MediaImage
from mediaroomio.serializers import GlobalMediaImageConnectorSlimSerializer

from notificationio.models import Notification
from notificationio.services import NotificationService
from notificationio.utils import changed_fields_with_values

from tagio.choices import TagEntity
from tagio.models import Tag, TagConnector
from tagio.rest.serializers.tags import PrivateTagThroughSerializer

logger = logging.getLogger(__name__)


class PrivateProductSerializer(serializers.ModelSerializer):
    tags = PrivateTagThroughSerializer(
        read_only=True, many=True, source="tagconnector_set"
    )
    tag_names = serializers.ListField(
        child=serializers.CharField(),
        max_length=255,
        write_only=True,
        required=False,
    )
    merchant = serializers.HiddenField(default=serializers.CurrentUserDefault())
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    base_product = serializers.SlugRelatedField(
        queryset=BaseProduct.objects.filter()
        .filter(merchant_product__isnull=True)
        .all(),
        write_only=True,
        slug_field="uid",
        allow_null=True,
        allow_empty=True,
        required=False,
        help_text="If you do not have base product, so do not send the base_product to server.",
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.filter(),
        slug_field="uid",
        allow_empty=True,
        required=False,
        allow_null=True,
    )

    active_ingredients = serializers.SlugRelatedField(
        queryset=Ingredient.objects.filter(),
        many=True,
        slug_field="uid",
        allow_empty=True,
        required=False,
        allow_null=True,
    )
    dosage_form = serializers.SlugRelatedField(
        queryset=DosageForm.objects.filter(),
        allow_empty=True,
        allow_null=True,
        required=False,
        slug_field="uid",
    )
    manufacturer = serializers.SlugRelatedField(
        queryset=Manufacturer.objects.filter(),
        allow_empty=True,
        allow_null=True,
        required=False,
        slug_field="uid",
    )
    brand = serializers.SlugRelatedField(
        queryset=Brand.objects.filter(),
        slug_field="uid",
        allow_empty=True,
        required=False,
        allow_null=True,
    )
    route_of_administration = serializers.SlugRelatedField(
        queryset=RouteOfAdministration.objects.filter(),
        slug_field="uid",
        allow_empty=True,
        required=False,
        allow_null=True,
    )
    medicine_physical_state = serializers.SlugRelatedField(
        queryset=MedicinePhysicalState.objects.filter(),
        slug_field="uid",
        allow_empty=True,
        required=False,
        allow_null=True,
    )
    description = serializers.CharField(
        max_length=255,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    primary_image = VersatileImageFieldSerializer(
        allow_null=True,
        allow_empty_file=True,
        read_only=True,
        sizes=[
            ("original", "url"),
            ("at256", "crop__256x256"),
            ("at512", "crop__512x512"),
        ],
    )
    image = VersatileImageFieldSerializer(
        allow_null=True,
        allow_empty_file=True,
        required=False,
        write_only=True,
        sizes=[
            ("original", "url"),
            ("at256", "crop__256x256"),
            ("at512", "crop__512x512"),
        ],
    )
    additional_images = serializers.ListField(
        child=VersatileImageFieldSerializer(
            allow_null=True,
            allow_empty_file=True,
            write_only=True,
            sizes=[
                ("original", "url"),
                ("at256", "crop__256x256"),
                ("at512", "crop__512x512"),
            ],
        ),
        write_only=True,
        required=False,
        allow_null=True,
        allow_empty=True,
    )

    unit = serializers.CharField(
        max_length=50, read_only=True, source="base_product.unit"
    )
    strength = serializers.CharField(
        max_length=50, read_only=True, source="base_product.strength"
    )
    strength_name = serializers.CharField(
        max_length=50,
        write_only=True,
        allow_blank=True,
        allow_null=True,
        required=False,
    )

    total_images = GlobalMediaImageConnectorSlimSerializer(many=True, read_only=True)
    stock_status = serializers.CharField(read_only=True)
    is_created_by_merchant = serializers.BooleanField(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["name"] = instance.base_product.name
        data["description"] = (
            instance.base_product.description
            if instance.base_product.description
            else ""
        )
        data["dosage_form"] = (
            instance.base_product.dosage_form.name
            if instance.base_product.dosage_form
            else ""
        )
        data["brand"] = (
            instance.base_product.brand.name if instance.base_product.brand else ""
        )
        data["category"] = (
            instance.base_product.category.name
            if instance.base_product.category
            else ""
        )
        data["active_ingredients"] = [
            ingredient.name
            for ingredient in instance.base_product.active_ingredients.all()
        ]
        data["manufacturer"] = (
            instance.base_product.manufacturer.name
            if instance.base_product.manufacturer
            else ""
        )
        data["route_of_administration"] = (
            instance.base_product.route_of_administration.name
            if instance.base_product.route_of_administration
            else ""
        )
        data["medicine_physical_state"] = (
            instance.base_product.medicine_physical_state.name
            if instance.base_product.medicine_physical_state
            else ""
        )

        return data

    class Meta:
        model = Product
        fields = (
            "uid",
            "base_product",
            "name",
            "stock",
            "unit",
            "strength",
            "strength_name",
            "buying_price",
            "selling_price",
            "fraction_mrp",
            "discount_price",
            "final_price",
            "merchant",
            "image",
            "additional_images",
            "status",
            "manufacturer",
            "brand",
            "medicine_physical_state",
            "dosage_form",
            "description",
            "category",
            "active_ingredients",
            "route_of_administration",
            "primary_image",
            "total_images",
            "tags",
            "tag_names",
            "stock_status",
            "is_created_by_merchant",
            "damage_stock",
            "box_type",
        )
        read_only_fields = ["final_price"]

    def validate(self, data):
        base_product = data.get("base_product")
        organization = data.get("merchant").get_organization()
        box_type = data.get("box_type")

        try:
            existing_product = Product.objects.get(
                base_product=base_product, organization=organization, box_type=box_type
            )
            raise serializers.ValidationError(
                {"detail": "This product already exists."}
            )
        except Product.DoesNotExist:
            return data

    def create(self, validated_data):
        with transaction.atomic():
            name = validated_data.pop("name", None)

            base_product = validated_data.pop("base_product", None)
            category = validated_data.pop("category", None)
            active_ingredients = validated_data.pop("active_ingredients", [])
            dosage_form = validated_data.pop("dosage_form", None)
            manufacturer = validated_data.pop("manufacturer", None)
            brand = validated_data.pop("brand", None)
            merchant = validated_data.get("merchant")
            fraction_mrp = validated_data.get("fraction_mrp", 0)
            selling_price = validated_data.get("selling_price", 0)
            route_of_administration = validated_data.pop(
                "route_of_administration", None
            )
            medicine_physical_state = validated_data.pop(
                "medicine_physical_state", None
            )
            additional_images = validated_data.pop("additional_images", [])
            description = validated_data.pop("description", None)
            tag_names_list = validated_data.pop("tag_names", [])
            strength = validated_data.pop("strength_name", "")
            create = False

            # checking if fraction mrp available or not. If available, customize the selling price.
            if fraction_mrp > 0:
                if base_product is not None:
                    if base_product.mrp:
                        selling_price = validated_data[
                            "selling_price"
                        ] = base_product.mrp * (fraction_mrp / Decimal(100))
                    else:
                        raise ValidationError(
                            {"fraction_mrp": "Your selected product has no MRP price."}
                        )
                else:
                    raise ValidationError(
                        {"fraction_mrp": "Please select a product to use MRP price."}
                    )
            # double check if selling price 0 or not
            if selling_price < 1:
                raise ValidationError("Please add selling price or fraction MRP.")

            """
            check if base product available or not
            if there is no base product, We will create base product and connect to that product to merchant product with flag.
            """
            if base_product is None:
                base_product = BaseProduct.objects.create(
                    name=name.title(),
                    description=description,
                    dosage_form=dosage_form,
                    manufacturer=manufacturer,
                    brand=brand,
                    category=category,
                    strength=strength,
                    route_of_administration=route_of_administration,
                    medicine_physical_state=medicine_physical_state,
                )
                create = True

                if active_ingredients:
                    for ingredient in active_ingredients:
                        base_product.active_ingredients.add(ingredient)
            validated_data["organization"] = merchant.get_organization()
            validated_data["base_product"] = base_product
            # saving the product
            instance = super().create(validated_data=validated_data)

            # adding images if available
            if type(additional_images) is list and additional_images:
                for image in additional_images:
                    media = MediaImage.objects.create(image=image)
                    MediaImageConnector.objects.create(
                        image=media,
                        product=instance,
                        kind=MediaImageConnectorKind.PRODUCT,
                    )

            tag_connectors = []
            if tag_names_list:
                for tag_name in tag_names_list:
                    tag, _ = Tag.objects.get_or_create(name=tag_name.lower())
                    try:
                        TagConnector.objects.get(product=instance, tag=tag)
                    except TagConnector.DoesNotExist:
                        tag_connectors.append(
                            TagConnector(
                                organization=merchant.get_organization(),
                                product=instance,
                                user=self.context["request"].user,
                                entity=TagEntity.PRODUCT,
                                tag=tag,
                            )
                        )

                TagConnector.objects.bulk_create(tag_connectors)

            if create:
                # if merchant create the base product, make a reference to base product that this is merchant product.
                base_product.merchant_product = instance
                base_product.save()

            # sending notification
            notification_service = NotificationService(request=self.context["request"])
            notification_service.create_notification_with_sending_notification_to_organization_users(
                previous_data={},
                saved_or_updated_instance=instance,
            )

            # adding current product to redis cache
            # product_redis = ProductRedisServices()
            # product_redis.save(pk=instance.pk, request=self.context["request"])

            # return the instance for response instance data
            return instance


class PrivateProductCountDetail(serializers.Serializer):
    total_in_stock = serializers.IntegerField(min_value=0)
    total_out_of_stock = serializers.IntegerField(min_value=0)


class PrivateProductOutOfStockSerializer(serializers.ModelSerializer):
    merchant = serializers.HiddenField(default=serializers.CurrentUserDefault())
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    base_product = serializers.SlugRelatedField(
        queryset=BaseProduct.objects.filter()
        .filter(merchant_product__isnull=True)
        .all(),
        slug_field="uid",
        allow_null=True,
        allow_empty=True,
        required=False,
        help_text="If you donot have base product, so do not send the base_product to server.",
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.filter(),
        slug_field="uid",
        allow_empty=True,
        required=False,
        allow_null=True,
    )

    active_ingredients = serializers.SlugRelatedField(
        queryset=Ingredient.objects.filter(),
        many=True,
        slug_field="uid",
        allow_empty=True,
        required=False,
        allow_null=True,
    )
    dosage_form = serializers.SlugRelatedField(
        queryset=DosageForm.objects.filter(),
        allow_empty=True,
        allow_null=True,
        required=False,
        slug_field="uid",
    )
    manufacturer = serializers.SlugRelatedField(
        queryset=Manufacturer.objects.filter(),
        allow_empty=True,
        allow_null=True,
        required=False,
        slug_field="uid",
    )
    brand = serializers.SlugRelatedField(
        queryset=Brand.objects.filter(),
        slug_field="uid",
        allow_empty=True,
        required=False,
        allow_null=True,
    )
    route_of_administration = serializers.SlugRelatedField(
        queryset=RouteOfAdministration.objects.filter(),
        slug_field="uid",
        allow_empty=True,
        required=False,
        allow_null=True,
    )
    medicine_physical_state = serializers.SlugRelatedField(
        queryset=MedicinePhysicalState.objects.filter(),
        slug_field="uid",
        allow_empty=True,
        required=False,
        allow_null=True,
    )
    description = serializers.CharField(
        max_length=255,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    primary_image = VersatileImageFieldSerializer(
        allow_null=True,
        allow_empty_file=True,
        read_only=True,
        sizes=[
            ("original", "url"),
            ("at256", "crop__256x256"),
            ("at512", "crop__512x512"),
        ],
    )
    image = VersatileImageFieldSerializer(
        allow_null=True,
        allow_empty_file=True,
        required=False,
        read_only=True,
        sizes=[
            ("original", "url"),
            ("at256", "crop__256x256"),
            ("at512", "crop__512x512"),
        ],
    )
    additional_images = serializers.ListField(
        child=VersatileImageFieldSerializer(
            allow_null=True,
            allow_empty_file=True,
            read_only=True,
            sizes=[
                ("original", "url"),
                ("at256", "crop__256x256"),
                ("at512", "crop__512x512"),
            ],
        ),
        read_only=True,
        required=False,
        allow_null=True,
        allow_empty=True,
    )
    unit = serializers.CharField(
        max_length=50, read_only=True, source="base_product.unit"
    )
    strength = serializers.CharField(
        max_length=50, read_only=True, source="base_product.strength"
    )

    total_images = GlobalMediaImageConnectorSlimSerializer(many=True, read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["name"] = instance.base_product.name
        data["description"] = (
            instance.base_product.description
            if instance.base_product.description
            else ""
        )
        data["dosage_form"] = (
            instance.base_product.dosage_form.name
            if instance.base_product.dosage_form
            else ""
        )
        data["brand"] = (
            instance.base_product.brand.name if instance.base_product.brand else ""
        )
        data["category"] = (
            instance.base_product.category.name
            if instance.base_product.category
            else ""
        )
        data["active_ingredients"] = [
            ingredient.name
            for ingredient in instance.base_product.active_ingredients.all()
        ]
        data["manufacturer"] = (
            instance.base_product.manufacturer.name
            if instance.base_product.manufacturer
            else ""
        )
        data["route_of_administration"] = (
            instance.base_product.route_of_administration.name
            if instance.base_product.route_of_administration
            else ""
        )
        data["medicine_physical_state"] = (
            instance.base_product.medicine_physical_state.name
            if instance.base_product.medicine_physical_state
            else ""
        )

        return data

    class Meta:
        model = Product
        fields = (
            "uid",
            "base_product",
            "name",
            "stock",
            "unit",
            "strength",
            "buying_price",
            "selling_price",
            "fraction_mrp",
            "discount_price",
            "final_price",
            "merchant",
            "image",
            "additional_images",
            "status",
            "manufacturer",
            "brand",
            "medicine_physical_state",
            "dosage_form",
            "description",
            "category",
            "active_ingredients",
            "route_of_administration",
            "primary_image",
            "total_images",
        )
        read_only_fields = ["__all__"]


class PrivateProductDetailSerializer(serializers.ModelSerializer):
    primary_image = VersatileImageFieldSerializer(
        allow_null=True,
        allow_empty_file=True,
        read_only=True,
        sizes=[
            ("original", "url"),
            ("at256", "crop__256x256"),
            ("at512", "crop__512x512"),
        ],
    )
    additional_images = serializers.ListField(
        child=VersatileImageFieldSerializer(
            allow_null=True,
            allow_empty_file=True,
            write_only=True,
            sizes=[
                ("original", "url"),
                ("at256", "crop__256x256"),
                ("at512", "crop__512x512"),
            ],
        ),
        write_only=True,
        required=False,
        allow_null=True,
        allow_empty=True,
        default=[],
    )
    manufacturer = serializers.StringRelatedField(
        source="base_product.manufacturer", read_only=True
    )
    manufacturer_uid = serializers.SlugRelatedField(
        write_only=True,
        queryset=Manufacturer.objects.filter(),
        slug_field="uid",
        allow_null=True,
        allow_empty=True,
    )
    name = serializers.CharField()
    brand = serializers.StringRelatedField(source="base_product.brand", read_only=True)
    brand_uid = serializers.SlugRelatedField(
        write_only=True,
        queryset=Brand.objects.filter(),
        slug_field="uid",
        allow_null=True,
        allow_empty=True,
    )
    medicine_physical_state = serializers.StringRelatedField(
        source="base_product.medicine_physical_state", read_only=True
    )
    medicine_physical_state_uid = serializers.SlugRelatedField(
        write_only=True,
        queryset=MedicinePhysicalState.objects.filter(),
        slug_field="uid",
        allow_null=True,
        allow_empty=True,
    )
    dosage_form = serializers.StringRelatedField(
        source="base_product.dosage_form", read_only=True
    )
    dosage_form_uid = serializers.SlugRelatedField(
        write_only=True,
        queryset=DosageForm.objects.filter(),
        slug_field="uid",
        allow_null=True,
        allow_empty=True,
    )
    description = serializers.CharField(allow_blank=True, allow_null=True)
    category = serializers.StringRelatedField(
        source="base_product.category", read_only=True
    )
    category_uid = serializers.SlugRelatedField(
        write_only=True,
        queryset=Category.objects.filter(),
        slug_field="uid",
        allow_null=True,
        allow_empty=True,
    )
    active_ingredients = serializers.StringRelatedField(
        source="base_product.active_ingredients", many=True, read_only=True
    )
    active_ingredients_uids = serializers.SlugRelatedField(
        write_only=True,
        queryset=Ingredient.objects.filter(),
        slug_field="uid",
        allow_null=True,
        allow_empty=True,
        many=True,
    )
    route_of_administration = serializers.CharField(
        source="base_product.route_of_administration", read_only=True
    )
    route_of_administration_uid = serializers.SlugRelatedField(
        write_only=True,
        queryset=RouteOfAdministration.objects.filter(),
        slug_field="uid",
        allow_null=True,
        allow_empty=True,
    )
    unit = serializers.CharField(
        max_length=50, read_only=True, source="base_product.unit"
    )
    fraction_mrp = serializers.IntegerField(default=0, allow_null=True)
    strength = serializers.CharField(
        max_length=50, read_only=True, source="base_product.strength"
    )
    total_images = GlobalMediaImageConnectorSlimSerializer(many=True, read_only=True)

    tag_names = serializers.ListField(
        child=serializers.CharField(),
        max_length=255,
        write_only=True,
        required=False,
    )
    merchant = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = PrivateTagThroughSerializer(
        read_only=True, many=True, source="tagconnector_set"
    )
    is_created_by_merchant = serializers.BooleanField(read_only=True)
    strength_name = serializers.CharField(write_only=True)

    class Meta:
        model = Product
        fields = (
            "uid",
            "name",
            "stock",
            "unit",
            "strength",
            "buying_price",
            "selling_price",
            "fraction_mrp",
            "discount_price",
            "final_price",
            "image",
            "total_images",
            "status",
            "primary_image",
            "manufacturer",
            "manufacturer_uid",
            "brand",
            "brand_uid",
            "medicine_physical_state",
            "medicine_physical_state_uid",
            "dosage_form",
            "dosage_form_uid",
            "description",
            "category",
            "category_uid",
            "active_ingredients",
            "active_ingredients_uids",
            "route_of_administration",
            "route_of_administration_uid",
            "additional_images",
            "tag_names",
            "merchant",
            "is_created_by_merchant",
            "tags",
            "box_type",
            "strength_name",
        )

        read_only_fields = ("primary_image", "final_price")
        write_only_fields = (
            "stock",
            "buying_price",
            "selling_price",
            "fraction_mrp",
            "discount_price",
            "image",
            "status",
            "additional_images",
            "box_type",
            "manufacturer_uid",
            "brand_uid",
            "medicine_physical_state_uid",
            "dosage_form_uid",
            "category_uid",
            "active_ingredients_uids",
            "route_of_administration_uid",
        )

    def update(self, instance: Product, validated_data):
        base_product = instance.base_product
        additional_images = validated_data.pop("additional_images", [])
        tag_names_list = validated_data.pop("tag_names", [])
        merchant = validated_data.get("merchant", self.context["request"].user)
        if "fraction_mrp" in validated_data and validated_data["fraction_mrp"] > 0:
            if base_product.mrp:
                fraction_mrp = validated_data["fraction_mrp"]
                selling_price = base_product.mrp * (fraction_mrp / Decimal(100))
                validated_data["selling_price"] = selling_price
            else:
                raise ValidationError(
                    {"fraction_mrp": "Your select product has no MRP price."}
                )
        # removed image when update
        if "image" in validated_data and validated_data["image"] and instance.image:
            instance.image.delete_all_created_images()
        changed_data = {}
        if base_product.merchant_product is not None:
            name = validated_data.get("name", "")
            strength = validated_data.get("strength_name", "")
            manufacturer: Manufacturer = validated_data.get("manufacturer_uid", None)
            brand: Brand = validated_data.get("brand_uid", None)
            medicine_physical_state: MedicinePhysicalState = validated_data.get(
                "medicine_physical_state_uid", None
            )
            dosage_form: DosageForm = validated_data.get("dosage_form_uid", None)
            description = validated_data.pop("description", "")
            ingredients = validated_data.get("active_ingredients_uids", [])
            category = validated_data.get("category_uid", None)
            # Update the manufacturer field of the base_product with the manufacturer_uid
            if len(name) > 0:
                changed_data["name"] = changed_fields_with_values(
                    "name", base_product.name, name
                )
                base_product.name = name

            if manufacturer is not None:
                changed_data["manufacturer"] = changed_fields_with_values(
                    "manufacturer", base_product.manufacturer, manufacturer
                )
                base_product.manufacturer = manufacturer

            if brand is not None:
                changed_data["brand"] = changed_fields_with_values(
                    "brand", base_product.brand, brand
                )
                base_product.brand = brand

            if medicine_physical_state is not None:
                changed_data["medicine_physical_state"] = changed_fields_with_values(
                    "medicine_physical_state",
                    base_product.medicine_physical_state,
                    medicine_physical_state,
                )
                base_product.medicine_physical_state = medicine_physical_state

            if dosage_form is not None:
                changed_data["dosage_form"] = changed_fields_with_values(
                    "dosage_form",
                    base_product.dosage_form,
                    dosage_form,
                )
                base_product.dosage_form = dosage_form

            if len(description) > 0:
                changed_data["description"] = changed_fields_with_values(
                    "description",
                    base_product.description,
                    description,
                )
                base_product.description = description

            if len(strength) > 0:
                changed_data["strength"] = changed_fields_with_values(
                    "strength",
                    base_product.strength,
                    strength,
                )
                base_product.strength = strength

            if ingredients:
                base_product.active_ingredients.set(ingredients)

            if category is not None:
                changed_data["category"] = changed_fields_with_values(
                    "category",
                    base_product.category,
                    category,
                )
                base_product.category = category
            base_product.save()

        instance.stock = validated_data.get("stock", instance.stock)
        instance.damage_stock = validated_data.get(
            "damage_stock", instance.damage_stock
        )
        instance.buying_price = validated_data.get(
            "buying_price", instance.buying_price
        )
        instance.selling_price = validated_data.get(
            "selling_price", instance.selling_price
        )
        instance.final_price = validated_data.get("final_price", instance.final_price)
        instance.fraction_mrp = validated_data.get(
            "fraction_mrp", instance.fraction_mrp
        )
        instance.discount_price = validated_data.get(
            "discount_price", instance.discount_price
        )
        instance.box_type = validated_data.get("box_type", instance.box_type)
        instance.status = validated_data.get("status", instance.status)
        changed_data = instance.get_dirty_fields(verbose=True)
        instance.save()

        if type(additional_images) is list and additional_images:
            for image in additional_images:
                media = MediaImage.objects.create(image=image)
                MediaImageConnector.objects.create(
                    image=media,
                    product=instance,
                    kind=MediaImageConnectorKind.PRODUCT,
                )

        # Get the existing tags associated with the product
        existing_tags = instance.tagconnector_set.values_list("tag__name", flat=True)

        # Find the tags to be removed
        tags_to_remove = existing_tags.exclude(tag__name__in=tag_names_list)

        # remove those tag names which are already in existing tags
        new_tag_names = [x for x in tag_names_list if x not in existing_tags]

        # Remove the TagConnector instances for the tags to be removed
        TagConnector.objects.filter(
            product=instance, tag__name__in=tags_to_remove
        ).delete()

        tag_connectors = []

        for tag_name in new_tag_names:
            tag, _ = Tag.objects.get_or_create(
                name=tag_name.lower(), defaults={"i18n": "en_EN"}
            )
            tag_connectors.append(
                TagConnector(
                    organization=merchant.get_organization(),
                    product=instance,
                    user=self.context["request"].user,
                    entity=TagEntity.PRODUCT,
                    tag=tag,
                )
            )

        # Bulk creates the new TagConnector instances
        TagConnector.objects.bulk_create(tag_connectors)

        product = (
            Product.objects.select_related(
                "base_product__manufacturer",
                "base_product__category",
                "base_product__brand",
                "base_product__route_of_administration",
                "base_product__medicine_physical_state",
            )
            .prefetch_related(
                "base_product__active_ingredients",
                "mediaimageconnector_set__image",
                "tagconnector_set__tag",
            )
            .get(id=instance.id)
        )
        # sending notification
        notification_service = NotificationService(
            request=self.context["request"],
            organization=instance.organization,
        )
        notification_service.create_notification_with_sending_notification_to_organization_users(
            previous_data=changed_data,
            saved_or_updated_instance=instance,
        )

        product.description = product.base_product.description
        product.name = product.base_product.name
        return product


class PrivateBulkProductDownloadSerializer(serializers.ModelSerializer):
    mrp = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        read_only=True,
        source="base_product.mrp",
    )
    name = serializers.CharField(source="base_product.name", read_only=True)

    class Meta:
        model = Product
        fields = ["uid", "name", "mrp", "discount_price", "stock"]


class PrivateBulkProductUpdateSerializer(serializers.Serializer):
    file = serializers.FileField(
        validators=[FileExtensionValidator(allowed_extensions=["xlsx"])],
        write_only=True,
    )
    merchant = serializers.HiddenField(default=serializers.CurrentUserDefault())
    message = serializers.CharField(read_only=True)

    def create(self, validated_data):
        excel_file = validated_data.pop("file", None)
        merchant = validated_data.get("merchant", "")
        organization: Organization = self.context["request"].user.get_organization()

        if excel_file:
            df = pd.read_excel(excel_file)
            df[["Strength"]] = df.loc[:, ["Strength"]].fillna(value="")
            df["description"] = ""
            message = "Successful"
            product_update_list = []
            for index, row in df.iterrows():
                try:
                    if not isinstance(row["Brand"], float) and not isinstance(
                        row["Strength"], float
                    ):
                        product_name = " ".join([row["Brand"].lower(), row["Strength"]])
                        product_name = product_name.lstrip()
                    else:
                        product_name = row["Name"]

                    box_type = (
                        row["Box type"] if row["Box type"] else ProductBoxType.WITH_BOX
                    )

                    try:
                        product = Product.objects.get(
                            base_product__name__istartswith=product_name,
                            organization=organization,
                            box_type=box_type,
                        )
                        # Update existing product
                        product.selling_price = row["MRP"]
                        product.final_price = row["MRP"] * (1 - row["Discount"] / 100)
                        product.discount_price = row["Discount"]
                        product.stock = row["Stock"]
                        product_update_list.append(product)
                        df.drop(index, inplace=True)

                    except Product.MultipleObjectsReturned:
                        product = Product.objects.filter(
                            base_product__name=product_name,
                            organization=organization,
                            box_type=box_type,
                        )
                        product = product.first()
                        # Update existing product
                        product.selling_price = row["MRP"]
                        product.final_price = row["MRP"] * (1 - row["Discount"] / 100)
                        product.discount_price = row["Discount"]
                        product.stock = row["Stock"]
                        product_update_list.append(product)
                        df.drop(index, inplace=True)

                    except Product.DoesNotExist:
                        try:
                            base_products = BaseProduct.objects.filter(
                                brand__name__iexact=row["Brand"].lower()
                                if not isinstance(row["Brand"], float)
                                else ""
                            )

                            if base_products:
                                strength = (
                                    row["Strength"].lower()
                                    if not isinstance(row["Strength"], float)
                                    else ""
                                )
                                match = re.search(r"\d+", str(strength))
                                result_re = match.group()
                                if result_re:
                                    base_products = base_products.filter(
                                        strength__icontains=result_re
                                    )

                                    if base_products:
                                        if not (isinstance(row["Dosage Form"], float)):
                                            base_products = base_products.filter(
                                                dosage_form__name__icontains=row[
                                                    "Dosage Form"
                                                ].lower()
                                                if not isinstance(
                                                    row["Dosage Form"], float
                                                )
                                                else ""
                                            )
                                            if not base_products:
                                                message = "Dosage form name not found"
                                        else:
                                            message = "Dosage form name not found"

                                    else:
                                        message = "Strength name not found"

                            else:
                                message = "Brand name not found"
                                row["description"] = message

                            base_products = base_products.first()

                            if base_products:
                                Product.objects.create(
                                    base_product=base_products,
                                    merchant=merchant,
                                    organization=organization,
                                    selling_price=0
                                    if isinstance(row["MRP"], float)
                                    else decimal.Decimal(row["MRP"]),
                                    discount_price=0
                                    if isinstance(row["Discount"], float)
                                    else decimal.Decimal(row["Discount"]),
                                    stock=row["Stock"],
                                    box_type=row["Box type"]
                                    if not isinstance(row["Box type"], float)
                                    else ProductBoxType.WITH_BOX,
                                )

                                df.drop(index, inplace=True)
                            else:
                                message = "some base product not found"
                                df.loc[index, "description"] = message
                        except Exception as e:
                            logger.warning("UPLOAD file -> ", e)
                            message = "some base product not found"

                except Exception as e:
                    logger.warning("Finally file -> ", e)

            if len(product_update_list) > 0:
                try:
                    Product.objects.bulk_update(
                        product_update_list,
                        fields=[
                            "stock",
                            "selling_price",
                            "final_price",
                            "discount_price",
                        ],
                    )

                except Exception as e:
                    logger.warning("UPLOAD file -> ", e)

            validated_data["message"] = message
        return validated_data
