from django.urls import path

from ..views import organizations

urlpatterns = [
    path(
        "/default",
        organizations.PrivateOrganizationInfoDetail.as_view(),
        name="organization-info-detail",
    ),
    path(
        "/address/districts",
        organizations.PrivateAddressDistrictList.as_view(),
        name="organization-address_district-list",
    ),
    path(
        "/detail",
        organizations.PrivateOrganizationDetail.as_view(),
        name="organization-detail",
    ),
    path(
        "/product/categories",
        organizations.PrivateProductCategoriesList.as_view(),
        name="organization-product-category-list",
    ),
    path(
        "/<uuid:uid>",
        organizations.PrivateOrganizationDetail.as_view(),
        name="organization-detail",
    ),
    path("", organizations.PrivateOrganizationList.as_view(), name="organization-list"),
]
