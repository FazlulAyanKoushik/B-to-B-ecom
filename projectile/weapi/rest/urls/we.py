from django.urls import path

from ..views import we

urlpatterns = [
    path(
        "",
        we.PrivateOrganizationDetail.as_view(),
        name="organization-detail",
    ),
]
