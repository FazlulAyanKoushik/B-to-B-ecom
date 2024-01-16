from django.urls import path

from weapi.rest.views import addresses


urlpatterns = [
    path(
        "/customer/<uuid:uid>",
        addresses.PrivateCustomerAddressDetail.as_view(),
        name="customer-address-detail",
    ),
    path(
        "/customer",
        addresses.PrivateCustomerAddressList.as_view(),
        name="customer-address-list",
    ),
    path(
        "/<uuid:uuid>",
        addresses.PrivateOrganizationAddressDetail.as_view(),
        name="organization-address-detail",
    ),
    path(
        "",
        addresses.PrivateOrganizationAddressList.as_view(),
        name="organization-address-list",
    ),
]
