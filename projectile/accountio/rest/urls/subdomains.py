from django.urls import path

from ..views import domains

urlpatterns = [
    path(
        "/<str:domain_name>",
        domains.CheckDomainAvailability.as_view(),
        name="domain-availability-check",
    )
]
