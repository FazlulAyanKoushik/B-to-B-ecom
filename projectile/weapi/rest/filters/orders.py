from django_filters import rest_framework as filters

from orderio.models import Order


class FilterOrders(filters.FilterSet):
    date = filters.DateFromToRangeFilter(field_name="created_at")
    total_price = filters.RangeFilter()

    class Meta:
        model = Order
        fields = ["date", "total_price"]
