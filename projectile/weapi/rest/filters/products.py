from django_filters import rest_framework as filters

from catalogio.models import (
    Category,
    Manufacturer,
    Product,
    DosageForm,
)


class FilterProducts(filters.FilterSet):
    final_price = filters.RangeFilter()

    class Meta:
        model = Product
        fields = [
            "final_price",
            "status",
        ]


class PrivateProductFilter(filters.FilterSet):
    category = filters.ModelChoiceFilter(
        queryset=Category.objects.filter(),
        to_field_name="slug",
        field_name="base_product__category__slug",
    )
    dosage_form = filters.ChoiceFilter(
        field_name="base_product__dosage_form__slug",
        choices=DosageForm.objects.filter().values_list(
            "slug",
            "name",
        ),
    )
    manufacturer = filters.ChoiceFilter(
        field_name="base_product__manufacturer__slug",
        choices=Manufacturer.objects.filter().values_list(
            "slug",
            "name",
        ),
    )

    class Meta:
        model = Product
        fields = (
            "category",
            "dosage_form",
            "manufacturer",
        )
