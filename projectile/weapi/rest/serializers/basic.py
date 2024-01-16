from rest_framework import serializers

from catalogio.models import (
    Brand,
    Category,
    Ingredient,
    RouteOfAdministration,
    MedicinePhysicalState,
    Manufacturer,
    DosageForm,
)


class PrivateBasicBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("uid", "name", "slug")
        read_only_fields = ("uid", "slug")


class PrivateBasicCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("uid", "name", "slug")
        read_only_fields = ("uid", "slug")


class PrivateBasicIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("uid", "name", "slug")
        read_only_fields = ("uid", "slug")


class PrivateBasicRouteOfAdministrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteOfAdministration
        fields = ("uid", "name", "slug")
        read_only_fields = ("uid", "slug")


class PrivateBasicMedicinePhysicalStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicinePhysicalState
        fields = ("uid", "name", "slug")
        read_only_fields = ("uid", "slug")


class PrivateBasicDosageFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = DosageForm
        fields = ("uid", "name", "slug")
        read_only_fields = ("uid", "slug")


class PrivateBasicManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ("uid", "name", "slug")
        read_only_fields = ("uid", "slug")
