from django.urls import path

from ..views import payments

urlpatterns = [
    path("", payments.GlobalPaymentMethodList.as_view(), name="payments-list"),
]
