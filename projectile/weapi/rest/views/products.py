import pandas as pd
import uuid

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import (
    Case,
    When,
    Value,
    CharField,
    BooleanField,
)
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework import status
from rest_framework.generics import (
    get_object_or_404,
    ListCreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    CreateAPIView,
)
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from catalogio.choices import ProductStatus
from catalogio.models import Product, BaseProduct

from ..filters.products import FilterProducts
from ..permissions import IsOrganizationStaff, IsOrganizationAdmin
from ..serializers.organizations import PrivateProductBulkDiscountSerializer
from ..serializers.products import (
    PrivateProductDetailSerializer,
    PrivateProductSerializer,
    PrivateProductOutOfStockSerializer,
    PrivateBulkProductUpdateSerializer,
    PrivateBulkProductDownloadSerializer,
    PrivateProductCountDetail,
)


@extend_schema(
    description="Example: http://127.0.0.1:8000/api/v1/we/products?category=analgesics&dosage-form=oral&manufacturer=manufacturers3",
    parameters=[
        OpenApiParameter(
            "manufacturer",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="single manufacturer slug only URL?manufacturer=manufacturer1",
        ),
        OpenApiParameter(
            "category",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="Single category slug ex: URL?category=category1",
        ),
        OpenApiParameter(
            "dosage-form",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="Single dosage-form slug only ex: URL?dosage-form=oral",
        ),
        OpenApiParameter(
            name="final_price_min",
            description="Min Final Price (merchant MRP with discount)",
            type=str,
        ),
        OpenApiParameter(
            name="final_price_max",
            description="Max Final Price (merchant MRP with discount)",
            type=str,
        ),
        OpenApiParameter(
            "search",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="Search by product name, active ingredient and unit",
        ),
        OpenApiParameter(
            "status",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="filter by product status: DRAFT, PUBLISHED, UNPUBLISHED, ARCHIVED, HIDDEN",
        ),
    ],
)
class PrivateProductList(ListCreateAPIView):
    serializer_class = PrivateProductSerializer
    permission_classes = [IsOrganizationStaff]

    filter_backends = [DjangoFilterBackend]
    filterset_class = FilterProducts

    def get_queryset(self):
        products = (
            self.request.user.get_organization()
            .product_set.select_related(
                "base_product",
                "base_product__manufacturer",
                "base_product__category",
                "base_product__brand",
                "base_product__route_of_administration",
                "base_product__medicine_physical_state",
            )
            .prefetch_related(
                "base_product__active_ingredients",
                "mediaimageconnector_set__image",
                "tagconnector_set__tag",
            )
            .annotate(
                stock_status=Case(
                    When(stock__gte=10, then=Value("In_Stock")),
                    When(stock__gt=0, then=Value("Low")),
                    default=Value("Out_Of_Stock"),
                    output_field=CharField(),
                )
            )
            .annotate(
                is_created_by_merchant=Case(
                    When(base_product__merchant_product__isnull=True, then=False),
                    default=True,
                    output_field=BooleanField(),
                )
            )
            .order_by("-created_at")
            .get_status_editable()
        )

        # filter by category
        category = self.request.query_params.get("category", "")
        if category:
            products = products.filter(base_product__category__slug=category)

        # filter by dosage form
        dosage_form = self.request.query_params.get("dosage-form", "")
        if dosage_form:
            products = products.filter(base_product__dosage_form__slug=dosage_form)

        # filter by manufacturer
        manufacturer = self.request.query_params.get("manufacturer", "")
        if manufacturer:
            products = products.filter(base_product__manufacturer__slug=manufacturer)

        # search
        search = self.request.query_params.get("search", "")
        if search:
            products = products.filter(base_product__name__istartswith=search)

        # search by unit
        unit_search = self.request.query_params.get("unit", "")
        if unit_search:
            products = products.filter(base_product__unit__istartswith=unit_search)

        # filter by stock
        stock = self.request.query_params.get("stock", "")
        if stock:
            if stock == "in-stock":
                products = products.filter(stock__gt=0)
            else:
                products = products.filter(stock__lte=0)

        return products

    def create(self, request, *args, **kwargs):
        additionalimage = request.data.get("additional_images", [])
        if not isinstance(additionalimage, InMemoryUploadedFile):
            if "additional_images" in request.data and "_mutable" in request.data:
                request.data._mutable = True
                del request.data["additional_images"]
                request.data._mutable = False

        return super().create(request=request, *args, **kwargs)


@extend_schema(
    description="The product can be viewed by admin, owner, manager, and staff. Only admin or owner can update or remove the product."
)
class PrivateProductDetail(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.get_status_editable()
    serializer_class = PrivateProductDetailSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsOrganizationAdmin()]
        else:
            return [IsOrganizationStaff()]

    def get_object(self):
        product = get_object_or_404(
            self.queryset.select_related(
                "base_product__manufacturer",
                "base_product__category",
                "base_product__brand",
                "base_product__route_of_administration",
                "base_product__medicine_physical_state",
            )
            .prefetch_related(
                "base_product__active_ingredients",
                "mediaimageconnector_set__image",
                "tagconnector_set__tag",
            )
            .filter(
                organization=self.request.user.get_organization(),
            )
            .annotate(
                is_created_by_merchant=Case(
                    When(base_product__merchant_product__isnull=True, then=False),
                    default=True,
                    output_field=BooleanField(),
                )
            ),
            uid=self.kwargs.get("uuid"),
        )
        product.description = product.base_product.description
        product.name = product.base_product.name
        product.unit = product.base_product.unit
        return product

    def perform_destroy(self, instance):
        instance.status = ProductStatus.REMOVED
        instance.save()

    def update(self, request, *args, **kwargs):
        additionalimage = request.data.get("additional_images", [])
        if not isinstance(additionalimage, InMemoryUploadedFile):
            if "additional_images" in request.data:
                request.data._mutable = True
                del request.data["additional_images"]
                request.data._mutable = False

        return super().update(request=request, *args, **kwargs)


class PrivateProductBulkDiscount(UpdateAPIView):
    serializer_class = PrivateProductBulkDiscountSerializer
    http_method_names = ("put",)
    permission_classes = [IsOrganizationStaff]

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=200)


class PrivateStockCountDetail(RetrieveAPIView):
    permission_classes = [IsOrganizationStaff]
    serializer_class = PrivateProductCountDetail

    def get_object(self):
        organization = self.request.user.get_organization()
        organization_products = Product.objects.get_status_editable().filter(
            organization=organization
        )

        return {
            "total_in_stock": organization_products.filter(stock__gt=0).count(),
            "total_out_of_stock": organization_products.filter(stock=0).count(),
        }


class PrivateProductOutOfStockList(ListAPIView):
    queryset = Product.objects.get_status_editable()
    permission_classes = [IsOrganizationStaff]
    serializer_class = PrivateProductOutOfStockSerializer

    def get(self, request, *args, **kwargs):
        products = (
            self.queryset.select_related(
                "base_product",
                "base_product__manufacturer",
                "base_product__category",
                "base_product__brand",
                "base_product__route_of_administration",
                "base_product__medicine_physical_state",
            )
            .prefetch_related(
                "base_product__active_ingredients",
                "mediaimageconnector_set__image",
            )
            .filter(organization=request.user.get_organization(), stock=0)
            .order_by("base_product__name")
        )

        stock_out = products.count()

        response_data = {
            "count": stock_out,
            "products": self.serializer_class(products, many=True).data,
        }

        return Response(response_data)


@extend_schema(
    description="format be like: Name [index] -> Form [0] - Brand [1] - Strength [2] - MRP [3] - Discount [4] - Stock [5]"
)
class PrivateProductBulkUpdate(CreateAPIView):
    parser_classes = (FormParser, MultiPartParser)
    serializer_class = PrivateBulkProductUpdateSerializer
    permission_classes = [IsOrganizationStaff]
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class PrivateProductBulkDownload(ListAPIView):
    serializer_class = PrivateBulkProductDownloadSerializer
    permission_classes = [IsOrganizationStaff]

    def get(self, request, *args, **kwargs):
        organization = self.request.user.get_organization()
        products = Product.objects.select_related(
            "base_product__dosage_form",
            "base_product__brand",
        ).filter(organization=organization)

        # Set up response object with appropriate Excel header
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        unique_file_name = str(uuid.uuid4())
        response[
            "Content-Disposition"
        ] = f'attachment; filename="{unique_file_name}.xlsx"'

        # Create a DataFrame with the product data
        data = []
        header_row = [
            "Name",
            "Category",
            "Dosage Form",
            "Brand",
            "Strength",
            "MRP",
            "Discount",
            "Stock",
            "Box type",
        ]
        data.append(header_row)

        # add products to array with data serially
        for product in products:
            data_row = [
                product.base_product.name
                if product.base_product.name is not None
                else "",
                product.base_product.category.name
                if product.base_product.category is not None
                else "",
                product.base_product.dosage_form.name
                if product.base_product.dosage_form is not None
                else "",
                product.base_product.brand.name
                if product.base_product.brand is not None
                else "",
                product.base_product.strength,
                product.selling_price,
                product.discount_price,
                product.stock,
                product.box_type,
            ]
            data.append(data_row)

        # Convert the data to a pandas DataFrame
        df = pd.DataFrame(data)

        # Save the DataFrame to Excel format
        df.to_excel(response, index=False, header=False)

        return response
