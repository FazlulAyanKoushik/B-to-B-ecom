from rest_framework import serializers
from versatileimagefield.serializers import VersatileImageFieldSerializer

from addressio.models import (
    Address,
    District,
    Division,
    Upazila,
)
from addressio.rest.serializers.addresses import (
    GlobalDistrictSerializer,
    GlobalUpazilaSerializer,
    GlobalDivisionSerializer,
)


class PrivateAddressesListDetailSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    upazila = GlobalUpazilaSerializer(read_only=True)
    district = GlobalDistrictSerializer(read_only=True)
    division = GlobalDivisionSerializer(read_only=True)
    country = serializers.CharField(default="Bangladesh")
    upazila_uid = serializers.SlugRelatedField(
        queryset=Upazila.objects.filter().order_by("name"),
        slug_field="uid",
        allow_null=True,
        allow_empty=True,
        write_only=True,
    )
    district_uid = serializers.SlugRelatedField(
        queryset=District.objects.filter().order_by("name"),
        slug_field="uid",
        allow_null=True,
        allow_empty=True,
        write_only=True,
    )
    division_uid = serializers.SlugRelatedField(
        queryset=Division.objects.filter().order_by("name"),
        slug_field="uid",
        allow_null=True,
        allow_empty=True,
        write_only=True,
    )

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
            "user",
            # write_only_fields
            "upazila_uid",
            "district_uid",
            "division_uid",
            "is_storefront",
        )

    def create(self, validated_data):
        validated_data["upazila"] = validated_data.pop("upazila_uid", None)
        validated_data["district"] = validated_data.pop("district_uid", None)
        validated_data["division"] = validated_data.pop("division_uid", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data["upazila"] = validated_data.pop("upazila_uid", instance.upazila)
        validated_data["district"] = validated_data.pop(
            "district_uid", instance.district
        )
        validated_data["division"] = validated_data.pop(
            "division_uid", instance.division
        )
        return super().update(instance=instance, validated_data=validated_data)


class GlobalOrganizationFromDomainSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=500, allow_blank=True, read_only=True)
    logo = VersatileImageFieldSerializer(
        allow_null=True,
        allow_empty_file=True,
        read_only=True,
        sizes=[
            ("original", "url"),
            ("at256", "crop__256x256"),
            ("at512", "crop__512x512"),
        ],
    )
