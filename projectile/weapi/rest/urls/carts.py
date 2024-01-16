from django.urls import path
from weapi.rest.views import carts

urlpatterns = [
    path(
        "/<slug:product_slug>",
        carts.PrivateCartDetail.as_view(),
        name="cart_product-remove",
    ),
    path("", carts.PrivateCartList.as_view(), name="cart_product-list"),
]
