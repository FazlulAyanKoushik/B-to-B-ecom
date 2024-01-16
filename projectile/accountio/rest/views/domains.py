from drf_spectacular.utils import extend_schema, OpenApiResponse

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accountio.models import Organization


class CheckDomainAvailability(APIView):
    @extend_schema(
        description="This API will check if domain is available or not.",
        responses={
            200: OpenApiResponse(response=None, description="Domain is available."),
            204: OpenApiResponse(response=None, description="Domain is not available."),
        },
    )
    def get(self, request, *args, **kwargs):
        try:
            Organization.objects.get(domain=self.kwargs.get("domain_name"))
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Organization.DoesNotExist:
            return Response(status=status.HTTP_200_OK)
