from django.urls import path

from ..views import register

urlpatterns = [
    path(
        "/registration",
        register.GlobalUserRegistrationList.as_view(),
        name="user-registration",
    ),
    path(
        "/organization/registration",
        register.GlobalOrganizationRegister.as_view(),
        name="organization.registration",
    ),
]
