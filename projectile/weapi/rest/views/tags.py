from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import filters

from tagio.models import Tag

from ..permissions import IsOrganizationStaff
from ..serializers.tags import PrivateTagSerializer


class PrivateTagList(ListCreateAPIView):
    queryset = Tag.objects.filter()
    serializer_class = PrivateTagSerializer
    permission_classes = [IsOrganizationStaff]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        return Tag.objects.filter()


class PrivateTagDetail(RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.filter()
    serializer_class = PrivateTagSerializer
    permission_classes = [IsOrganizationStaff]
    lookup_field = "uid"
