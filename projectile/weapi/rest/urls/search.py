from django.urls import path

from ..views import search

urlpatterns = [
    path(
        "/products",
        search.PrivateBaseProductSearch.as_view(),
        name="search-base.product",
    ),
    path(
        "/merchant/products",
        search.PrivateProductSearch.as_view(),
        name="search-product",
    ),
]
