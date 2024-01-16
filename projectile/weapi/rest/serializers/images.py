from rest_framework import serializers

from mediaroomio.models import MediaImage


class PrivateImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaImage
        fields = (
            "uid",
            "image",
            "caption",
            "copyright",
            "priority",
            "kind",
        )
