from django.urls import path

from ..views import products

urlpatterns = [
    path(
        "/out-of-stock",
        products.PrivateProductOutOfStockList.as_view(),
        name="product-out-of-stock-list",
    ),
    path(
        "/stock-status",
        products.PrivateStockCountDetail.as_view(),
        name="products-stock-detail",
    ),
    path(
        "/discount",
        products.PrivateProductBulkDiscount.as_view(),
        name="product-bulk-discount-by-filter",
    ),
    path(
        "/files/upload",
        products.PrivateProductBulkUpdate.as_view(),
        name="product-bulk-upload",
    ),
    path(
        "/files/download",
        products.PrivateProductBulkDownload.as_view(),
        name="product-bulk-download",
    ),
    path(
        "/<uuid:uuid>",
        products.PrivateProductDetail.as_view(),
        name="product-detail",
    ),
    path("", products.PrivateProductList.as_view(), name="products-list"),
]
