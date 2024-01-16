from django.urls import path, include

urlpatterns = [
    path("/addresses", include("weapi.rest.urls.addresses")),
    path("/carts", include("weapi.rest.urls.carts")),
    path("/products", include("weapi.rest.urls.products")),
    path("/search", include("weapi.rest.urls.search")),
    path("/basic", include("weapi.rest.urls.basic")),
    path("/orders", include("weapi.rest.urls.orders")),
    path("/dashboard", include("weapi.rest.urls.dashboards")),
    path("/customers", include("weapi.rest.urls.customers")),
    path("/tags", include("weapi.rest.urls.tags")),
    path("/images", include("weapi.rest.urls.images")),
    path("/users", include("weapi.rest.urls.users")),
    path("/delivery-charges", include("weapi.rest.urls.delivery_charges")),
    path("/inbox", include("weapi.rest.urls.inbox")),
    path("", include("weapi.rest.urls.organizations")),
]
