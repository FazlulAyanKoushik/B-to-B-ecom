import logging

from rest_framework import serializers

from tagio.models import Tag

logger = logging.getLogger(__name__)


class PrivateTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["uid", "parent", "category", "name", "i18n", "slug", "status"]
        read_only_fields = ("__all__",)
