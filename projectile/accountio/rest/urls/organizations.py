from django.urls import path

from ..views import organizations

urlpatterns = [
    path(
        "/<slug:slug>",
        organizations.PrivateOrganizationDetail.as_view(),
        name="organizations-details",
    ),
    path(
        "/<slug:slug>/addresses",
        organizations.PrivateOrganizationAddressList.as_view(),
        name="organizations-address-list",
    ),
    path(
        "/global/detail",
        organizations.GlobalOrganizationFromDomainDetail.as_view(),
        name="organization-global-detail-by-domain",
    ),
]
