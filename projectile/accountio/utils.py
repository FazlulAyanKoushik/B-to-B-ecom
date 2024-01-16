from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request

from accountio.models import Organization


def get_subdomain(request: Request) -> Organization:
    # checking of header is available or not.
    subdomain = request.headers.get("X-DOMAIN", None)
    if subdomain is None:
        raise NotFound(detail="Domain header is required.")

    # checking if that header is an appropriate domain or not.
    return get_object_or_404(
        Organization.objects.get_status_editable(), domain=subdomain
    )
