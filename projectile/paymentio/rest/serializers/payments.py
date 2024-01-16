from rest_framework import serializers

from paymentio.models import PaymentMethod


class GlobalPaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ("uid", "slug", "name")
        read_only_fields = ("__all__",)
