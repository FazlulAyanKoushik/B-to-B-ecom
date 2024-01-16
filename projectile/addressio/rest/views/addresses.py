from drf_spectacular.utils import extend_schema

from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from addressio.models import District, Division, Upazila

from ..serializers.addresses import (
    GlobalDistrictSerializer,
    GlobalDivisionSerializer,
    GlobalUpazilaSerializer,
)


@extend_schema(
    responses=GlobalDistrictSerializer,
)
class GlobalDistrictList(ListAPIView):
    serializer_class = GlobalDistrictSerializer
    queryset = District.objects.filter().order_by("name")
    permission_classes = [AllowAny]
    pagination_class = None


@extend_schema(
    responses=GlobalDivisionSerializer,
)
class GlobalDivisionList(ListAPIView):
    serializer_class = GlobalDivisionSerializer
    queryset = Division.objects.filter().order_by("name")
    permission_classes = [AllowAny]
    pagination_class = None


@extend_schema(
    responses=GlobalUpazilaSerializer,
)
class GlobalUpazilaList(ListAPIView):
    serializer_class = GlobalUpazilaSerializer
    queryset = Upazila.objects.filter().order_by("name")
    permission_classes = [AllowAny]
    pagination_class = None


@extend_schema(
    responses=GlobalDistrictSerializer,
)
class DistrictListByDivision(ListAPIView):
    serializer_class = GlobalDistrictSerializer
    permission_classes = [AllowAny]
    queryset = District.objects.filter().order_by("name")
    lookup_field = "division_uid"
    pagination_class = None

    def get_queryset(self):
        division_uid = self.kwargs.get("division_uid")
        queryset = District.objects.filter(division__uid=division_uid).order_by("name")
        return queryset


@extend_schema(
    responses=GlobalUpazilaSerializer,
)
class UpazilaListByDistrict(ListAPIView):
    serializer_class = GlobalUpazilaSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        district_uid = self.kwargs.get("district_uid")
        queryset = Upazila.objects.filter(district__uid=district_uid).order_by("name")
        return queryset
