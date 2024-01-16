from django.urls import path

from ..views import products

urlpatterns = [
    path(
        "/<slug:slug>",
        products.GlobalProductDetail.as_view(),
        name="global-product-detail",
    ),
    path("", products.GlobalProductSearchList.as_view(), name="global-product-list"),
]
