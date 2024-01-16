from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView

from catalogio.models import (
    Brand,
    Category,
    Ingredient,
    MedicinePhysicalState,
    Manufacturer,
    RouteOfAdministration,
    DosageForm,
)

from ..permissions import IsOrganizationStaff, IsOrganizationCustomer
from ..serializers.basic import (
    PrivateBasicBrandSerializer,
    PrivateBasicCategorySerializer,
    PrivateBasicDosageFormSerializer,
    PrivateBasicIngredientSerializer,
    PrivateBasicManufacturerSerializer,
    PrivateBasicMedicinePhysicalStateSerializer,
    PrivateBasicRouteOfAdministrationSerializer,
)


@extend_schema(
    parameters=[
        OpenApiParameter(
            "search",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="Search by name only",
        ),
    ],
    request=None,
    responses=PrivateBasicBrandSerializer,
)
class PrivateBrandList(ListCreateAPIView):
    permission_classes = [IsOrganizationStaff | IsOrganizationCustomer]
    serializer_class = PrivateBasicBrandSerializer
    queryset = Brand.objects.filter().order_by("name")
    filter_backends = [SearchFilter]
    search_fields = ["^slug"]
    pagination_class = None


@extend_schema(
    parameters=[
        OpenApiParameter(
            "search",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="Search by name only",
        ),
    ],
)
class PrivateCategoryList(ListCreateAPIView):
    permission_classes = [IsOrganizationStaff | IsOrganizationCustomer]
    serializer_class = PrivateBasicCategorySerializer
    queryset = Category.objects.filter().order_by("name")
    filter_backends = [SearchFilter]
    search_fields = ["^slug"]
    pagination_class = None


@extend_schema(
    parameters=[
        OpenApiParameter(
            "search",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="Search by name only",
        ),
    ],
)
class PrivateIngredientList(ListCreateAPIView):
    permission_classes = [IsOrganizationStaff | IsOrganizationCustomer]
    serializer_class = PrivateBasicIngredientSerializer
    queryset = Ingredient.objects.filter().order_by("name")
    filter_backends = [SearchFilter]
    search_fields = ["^slug"]
    pagination_class = None


@extend_schema(
    parameters=[
        OpenApiParameter(
            "search",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="Search by name only",
        ),
    ],
)
class PrivateRouteOfAdministrationList(ListCreateAPIView):
    permission_classes = [IsOrganizationStaff | IsOrganizationCustomer]
    serializer_class = PrivateBasicRouteOfAdministrationSerializer
    queryset = RouteOfAdministration.objects.filter().order_by("name")
    filter_backends = [SearchFilter]
    search_fields = ["^slug"]
    pagination_class = None


@extend_schema(
    parameters=[
        OpenApiParameter(
            "search",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="Search by name only",
        ),
    ],
)
class PrivateMedicinePhysicalStateList(ListCreateAPIView):
    permission_classes = [IsOrganizationStaff | IsOrganizationCustomer]
    serializer_class = PrivateBasicMedicinePhysicalStateSerializer
    queryset = MedicinePhysicalState.objects.filter().order_by("name")
    filter_backends = [SearchFilter]
    search_fields = ["^slug"]
    pagination_class = None


@extend_schema(
    parameters=[
        OpenApiParameter(
            "search",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="Search by name only",
        ),
    ],
)
class PrivateDosageFormList(ListCreateAPIView):
    permission_classes = [IsOrganizationStaff | IsOrganizationCustomer]
    serializer_class = PrivateBasicDosageFormSerializer
    queryset = DosageForm.objects.filter().order_by("name")
    filter_backends = [SearchFilter]
    search_fields = ["^slug"]
    pagination_class = None


@extend_schema(
    parameters=[
        OpenApiParameter(
            "search",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="Search by name only",
        ),
    ],
)
class PrivateManufacturerList(ListCreateAPIView):
    permission_classes = [IsOrganizationStaff | IsOrganizationCustomer]
    serializer_class = PrivateBasicManufacturerSerializer
    queryset = Manufacturer.objects.filter().order_by("name")
    filter_backends = [SearchFilter]
    search_fields = ["^slug"]
    pagination_class = None
