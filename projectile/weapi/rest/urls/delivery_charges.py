from django.urls import path

from ..views import delivery_charges

urlpatterns = [
    path(
        "/<uuid:address_uid>",
        delivery_charges.PrivateDeliveryCharge.as_view(),
        name="customer-order-delivery-charge",
    ),
    path(
        "",
        delivery_charges.PrivateDeliveryChargeList.as_view(),
        name="customer-order-delivery-charge-list",
    ),
]
