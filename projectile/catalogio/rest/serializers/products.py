from decimal import Decimal

from rest_framework import serializers

from versatileimagefield.serializers import VersatileImageFieldSerializer

from catalogio.models import Product

from mediaroomio.serializers import GlobalMediaImageConnectorSlimSerializer


class GlobalProductSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(source="base_product.name")
    description = serializers.StringRelatedField(source="base_product.description")
    category = serializers.StringRelatedField(source="base_product.category")
    active_ingredients = serializers.StringRelatedField(
        source="base_product.active_ingredients", many=True
    )
    dosage_form = serializers.StringRelatedField(source="base_product.dosage_form")
    manufacturer = serializers.StringRelatedField(source="base_product.manufacturer")
    brand = serializers.StringRelatedField(source="base_product.brand")
    total_images = GlobalMediaImageConnectorSlimSerializer(
        many=True, source="mediaimageconnector_set"
    )
    route_of_administration = serializers.StringRelatedField(
        source="base_product.route_of_administration"
    )
    medicine_physical_state = serializers.StringRelatedField(
        source="base_product.medicine_physical_state"
    )
    primary_image = VersatileImageFieldSerializer(
        sizes=[
            ("original", "url"),
            ("at256", "crop__256x256"),
            ("at512", "crop__512x512"),
        ],
        read_only=True,
    )
    unit = serializers.CharField(max_length=50, source="base_product.unit")
    strength = serializers.CharField(max_length=50, source="base_product.strength")
    final_price_with_offset = serializers.SerializerMethodField()
    total_discount = serializers.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Product
        fields = (
            "slug",
            "stock",
            "unit",
            "strength",
            "selling_price",
            "final_price",
            "discount_price",
            "name",
            "description",
            "category",
            "active_ingredients",
            "dosage_form",
            "manufacturer",
            "brand",
            "route_of_administration",
            "medicine_physical_state",
            "primary_image",
            "total_images",
            "box_type",
            "final_price_with_offset",
            "total_discount",
        )
        read_only_fields = ("__all__",)

    def get_final_price_with_offset(self, data):
        return data.selling_price * (1 - (data.total_discount / Decimal(100)))

    # def to_representation(self, instance):
    #     try:
    #         instance = super().to_representation(instance)
    #     except FileNotFoundError:
    #         instance.primary_image.delete_all_created_images()
    #         instance = super().to_representation(instance)
    #
    #     return instance
