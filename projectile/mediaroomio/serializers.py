from rest_framework import serializers
from versatileimagefield.serializers import VersatileImageFieldSerializer

from mediaroomio.models import MediaImage, MediaImageConnector


class GlobalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaImage
        fields = (
            "uid",
            "image",
            "width",
            "height",
            "ppoi",
            "caption",
            "copyright",
            "priority",
        )
        read_only_fields = ("__all__",)


class GlobalImageSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaImage
        fields = (
            "slug",
            "image",
        )
        read_only_fields = ("__all__",)


class GlobalMediaImageConnectorSlimSerializer(serializers.ModelSerializer):
    image = VersatileImageFieldSerializer(
        source="image.image",
        sizes=[
            ("original", "url"),
            ("at256", "crop__256x256"),
            ("at512", "crop__512x512"),
        ],
        read_only=True,
    )

    class Meta:
        model = MediaImageConnector
        fields = ("image",)
        read_only_fields = ("__all__",)
