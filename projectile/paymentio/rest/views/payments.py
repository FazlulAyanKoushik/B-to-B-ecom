from drf_spectacular.utils import extend_schema

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from paymentio.models import PaymentMethod
from paymentio.rest.serializers.payments import GlobalPaymentMethodSerializer


@extend_schema(
    responses=GlobalPaymentMethodSerializer,
)
class GlobalPaymentMethodList(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GlobalPaymentMethodSerializer
    queryset = PaymentMethod.objects.filter()
    pagination_class = None
