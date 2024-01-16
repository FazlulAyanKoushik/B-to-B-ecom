from rest_framework import serializers


class StatusSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)


class CountAndTotalSerializer(serializers.Serializer):
    ORDER_PLACED = StatusSerializer()
    ACCEPTED = StatusSerializer()
    PROCESSING = StatusSerializer()
    PACKAGING = StatusSerializer()
    PARTIAL_DELIVERY = StatusSerializer()
    WAITING_FOR_DELIVERER = StatusSerializer()
    ON_THE_WAY = StatusSerializer()
    PARTIAL_RETURNED = StatusSerializer()
    RETURNED = StatusSerializer()
    CANCELED = StatusSerializer()
    COMPLETED = StatusSerializer()


class CategorySerializer(serializers.Serializer):
    category_name = serializers.CharField()
    total_stock = serializers.IntegerField()


class ProductStockCountSerializer(serializers.Serializer):
    total_count = serializers.IntegerField(default=0)


class PrivateDashboardDetailSerializer(serializers.Serializer):
    total_order_count = serializers.IntegerField()
    count_and_total_by_status = CountAndTotalSerializer()
    customer_count = serializers.IntegerField()
    product_stock_price_sum = serializers.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    product_stock_count_sum = ProductStockCountSerializer()
    inventory_products_count = serializers.IntegerField()
    inventory_unique_products_count = serializers.IntegerField()
    categories_product = CategorySerializer(many=True)
    count_customer_with_advance_payment = serializers.IntegerField(read_only=True)
    count_customer_with_due_amount = serializers.IntegerField(read_only=True)
    customer_total_advance_payment = serializers.SerializerMethodField()
    customer_total_due_amount = serializers.SerializerMethodField()

    def get_customer_total_advance_payment(self, instance):
        customer_total_advance_payment = 0
        for advance in instance["advance"]:
            customer_total_advance_payment += advance.balance
        return customer_total_advance_payment

    def get_customer_total_due_amount(self, instance):
        customer_total_due_amount = 0

        for due in instance["due"]:
            customer_total_due_amount += due.balance

        return customer_total_due_amount
