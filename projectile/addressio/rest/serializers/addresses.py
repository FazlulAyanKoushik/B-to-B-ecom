from rest_framework import serializers

from addressio.models import District, Division, Upazila


class GlobalDistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = (
            "uid",
            "name",
        )
        read_only_fields = ("__all__",)


class GlobalDivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = (
            "uid",
            "name",
        )
        read_only_fields = ("__all__",)


class GlobalUpazilaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upazila
        fields = (
            "uid",
            "name",
        )
        read_only_fields = ("__all__",)
