from rest_framework.generics import RetrieveUpdateAPIView

from accountio.models import Organization
from weapi.rest import permissions
from weapi.rest.serializers.we import PrivateOrganizationDetailSerializer


class PrivateOrganizationDetail(RetrieveUpdateAPIView):
    queryset = Organization.objects.get_status_editable()
    serializer_class = PrivateOrganizationDetailSerializer
    permission_classes = [permissions.IsOrganizationStaff]
    ordering = ["-name"]

    def get_object(self):
        return self.request.user.get_organization()
