from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    model = serializers.SerializerMethodField()

    def get_model(self, instance):
        return self.Meta.model.__name__.upper()


class BasePublicSerializer(serializers.ModelSerializer):
    class Meta:
        read_only_fields = ("__all__",)
