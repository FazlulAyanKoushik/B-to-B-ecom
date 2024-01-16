from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from orderio.models import (
    Order,
    OrderProduct,
    OrderDelivery,
    Cart,
    CartProduct,
    ReturnOrderProduct,
)


class OrderProductInlineAdmin(admin.TabularInline):
    model = OrderProduct
    fk_name = "order"


class OrderDeliveryInlineAdmin(admin.TabularInline):
    model = OrderDelivery
    fk_name = "order"


@admin.register(Order)
class OrderAdmin(SimpleHistoryAdmin):
    model = Order
    list_display = [
        "serial_number",
        "uid",
        "customer",
        "total_price",
        "completed",
        "payment_method",
    ]
    inlines = (OrderProductInlineAdmin, OrderDeliveryInlineAdmin)


@admin.register(OrderProduct)
class OrderAdmin(SimpleHistoryAdmin):
    model = OrderProduct
    list_display = [
        "uid",
        "order",
        "product",
        "updated_quantity",
    ]


class CartProductInlineAdmin(admin.TabularInline):
    model = CartProduct
    fk_name = "cart"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    model = Cart
    list_display = [
        "uid",
        "customer",
        "total_price",
    ]
    inlines = [CartProductInlineAdmin]


@admin.register(ReturnOrderProduct)
class ReturnOrderProductAdmin(admin.ModelAdmin):
    model = ReturnOrderProduct
    list_display = [
        "uid",
        "order_product",
        "returned_quantity",
    ]


@admin.register(OrderDelivery)
class OrderDeliveryAdmin(admin.ModelAdmin):
    model = OrderDelivery
    list_display = [
        "uid",
        "order",
        "status",
        "stage",
    ]
    list_filter = ["status", "stage"]
