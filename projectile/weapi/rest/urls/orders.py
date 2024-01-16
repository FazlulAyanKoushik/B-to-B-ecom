from django.urls import path

from ..views import orders

urlpatterns = [
    path(
        "/<uuid:order_uid>/returns",
        orders.PrivateRerunOrderProduct.as_view(),
        name="return-order-product",
    ),
    path("/<uuid:uid>", orders.PrivateOrderDetail.as_view(), name="order-details"),
    path("", orders.PrivateOrderList.as_view(), name="orders-list"),
]
