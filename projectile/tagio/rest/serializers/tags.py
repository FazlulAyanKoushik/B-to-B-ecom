from rest_framework import serializers


class PrivateTagThroughSerializer(serializers.Serializer):
    uid = serializers.UUIDField(source="tag.uid")
    category = serializers.CharField(source="tag.category")
    name = serializers.CharField(source="tag.name")
    i18n = serializers.CharField(source="tag.i18n")
    slug = serializers.SlugField(source="tag.slug")
    status = serializers.CharField(source="tag.status")
