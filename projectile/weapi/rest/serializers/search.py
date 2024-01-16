from rest_framework import serializers

from versatileimagefield.serializers import VersatileImageFieldSerializer

from catalogio.models import BaseProduct


class PrivateBaseProductSearchSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    active_ingredients = serializers.StringRelatedField(many=True)
    dosage_form = serializers.StringRelatedField()
    manufacturer = serializers.StringRelatedField()
    brand = serializers.StringRelatedField()
    route_of_administration = serializers.StringRelatedField()
    medicine_physical_state = serializers.StringRelatedField()
    image = VersatileImageFieldSerializer(
        allow_null=True,
        allow_empty_file=True,
        read_only=True,
        sizes=[
            ("original", "url"),
            ("at256", "crop__256x256"),
            ("at512", "crop__512x512"),
        ],
    )

    class Meta:
        model = BaseProduct
        fields = (
            "uid",
            "name",
            "description",
            "category",
            "active_ingredients",
            "dosage_form",
            "manufacturer",
            "brand",
            "unit",
            "strength",
            "route_of_administration",
            "medicine_physical_state",
            "image",
            "mrp",
        )
        read_only_fields = ("__all__",)
