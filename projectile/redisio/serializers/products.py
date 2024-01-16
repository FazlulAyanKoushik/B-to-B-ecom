from rest_framework import serializers
from versatileimagefield.serializers import VersatileImageFieldSerializer

from catalogio.models import Product
from mediaroomio.serializers import GlobalMediaImageConnectorSlimSerializer
from tagio.rest.serializers.tags import PrivateTagThroughSerializer


class RedisProductsSerializer(serializers.ModelSerializer):
    tags = PrivateTagThroughSerializer(
        read_only=True, many=True, source="tagconnector_set"
    )
    total_images = GlobalMediaImageConnectorSlimSerializer(many=True, read_only=True)

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
    manufacturer = serializers.CharField(
        read_only=True, source="base_product.manufacturer.name", allow_blank=True
    )
    unit = serializers.CharField(
        read_only=True, source="base_product.unit", allow_blank=True
    )
    strength = serializers.CharField(
        read_only=True, source="base_product.strength", allow_blank=True
    )
    name = serializers.CharField(
        read_only=True, source="base_product.name", allow_blank=True
    )

    brand = serializers.CharField(
        read_only=True, source="base_product.brand.name", allow_blank=True
    )
    medicine_physical_state = serializers.CharField(
        read_only=True,
        source="base_product.medicine_physical_state.name",
        allow_blank=True,
    )
    description = serializers.CharField(
        read_only=True,
        source="base_product.description",
        allow_blank=True,
    )
    category = serializers.CharField(
        read_only=True,
        source="base_product.category.name",
        allow_blank=True,
    )
    dosage_form = serializers.CharField(
        read_only=True,
        source="base_product.dosage_form.name",
        allow_blank=True,
    )
    route_of_administration = serializers.CharField(
        read_only=True,
        source="base_product.route_of_administration.name",
        allow_blank=True,
    )

    active_ingredients = serializers.StringRelatedField(
        many=True, source="base_product.active_ingredients"
    )
    stock_status = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "uid",
            "slug",
            "name",
            "stock",
            "unit",
            "strength",
            "buying_price",
            "selling_price",
            "fraction_mrp",
            "discount_price",
            "final_price",
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
            "stock_status",
            "damage_stock",
            "box_type",
        )
