from rest_framework import serializers

from ...models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "uid",
            "rating",
            "feedback",
            "given_by",
            "organization",
            "product",
            "order",
        ]
