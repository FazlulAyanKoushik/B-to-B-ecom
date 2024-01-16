import decimal

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum, F, Case, When, Value, QuerySet

from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.exceptions import NotFound

from simple_history.models import HistoricalRecords

from accountio.models import Organization, OrganizationUser

from catalogio.models import Product

from common.utils import unique_number_generator

from core.utils import BaseModelwithUID

from orderio.choices import OrderDeliveryStatus, OrderStageChoices

User = get_user_model()


class Cart(BaseModelwithUID):
    customer = models.ForeignKey(User, related_name="cart", on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("customer", "organization")

    def total_price(self) -> decimal.Decimal:
        total_price = decimal.Decimal(0)
        if self.products.exists():
            for cart_product in self.products.all():
                total_price += cart_product.total_price()

            return total_price
        else:
            return decimal.Decimal(0)

    def __str__(self):
        return f"Customer: {self.customer}, Total price: {self.total_price()}"


class CartProduct(BaseModelwithUID):
    cart = models.ForeignKey(
        Cart,
        related_name="products",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product, related_name="product_carts", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    organization = models.ForeignKey(
        "accountio.Organization", on_delete=models.CASCADE, blank=True
    )

    def single_discounted_price(self):
        try:
            main_product = self.product
        except Product.DoesNotExist:
            self.delete()
            return decimal.Decimal(0)

        product_price = main_product.selling_price
        # get the all discounted percents
        product_discount_percent = main_product.discount_price
        customer_discount_offset_percent = self.organization.organizationuser_set.get(
            user=self.cart.customer
        ).discount_offset

        # sum the product discount and customer offset discount
        total_discount_percent = (
            product_discount_percent + customer_discount_offset_percent
        )

        # get the single product discounted price
        single_product_discounted_price = product_price * (
            1 - (total_discount_percent / decimal.Decimal(100))
        )
        return single_product_discounted_price

    def total_price(self) -> decimal.Decimal:
        single_product_discounted_price = self.single_discounted_price()
        # multiply the final product price with the quantity
        final_price = single_product_discounted_price * self.quantity

        return final_price

    class Meta:
        unique_together = ("cart", "product")
        ordering = ["-created_at"]

    def __str__(self):
        return f"CartProduct: {self.cart.customer.get_name()}, Product: {self.product.base_product.name}, Organization: {self.organization.name}"

    """
    In signal (orderio.signals):
    1. added an organization instance of self product organization.

    """


class Order(BaseModelwithUID):
    serial_number = models.PositiveIntegerField(blank=True, unique=True, editable=False)
    customer = models.ForeignKey(
        User, blank=True, on_delete=models.CASCADE, related_name="orders"
    )
    order_by = models.ForeignKey(User, blank=True, on_delete=models.CASCADE)
    organization = models.ForeignKey(
        "accountio.Organization", on_delete=models.CASCADE, blank=True
    )
    order_price = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2,
        help_text="This is a price which is initially created by a customer",
    )
    total_price = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2,
        help_text="This is include the discount_offset percent offer",
    )
    payable_amount = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2,
        help_text="This is the amount which will be paid by a customer",
    )
    discount_offset = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2,
        help_text="This is the customer special offer which is given by a organization.",
    )
    discount = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2,
        help_text="This is discount will appy on order total price, only accept percentage.",
    )
    address = models.JSONField()
    completed = models.BooleanField(default=False)
    note = models.TextField(blank=True)
    delivery_charge = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    receiver_name = models.CharField(max_length=150, blank=True)
    receiver_phone = PhoneNumberField(blank=True)
    payment_method = models.ForeignKey(
        "paymentio.PaymentMethod", on_delete=models.CASCADE
    )

    # history
    history = HistoricalRecords()

    def __str__(self):
        return f"Order ID: {self.serial_number}, Customer: {self.customer}, Total: {self.total_price}"

    def calculate_updated_price(self, delivery_charge=None):
        if delivery_charge is None:
            delivery_charge = self.delivery_charge

        total_discounted_price = 0

        order_products: QuerySet[OrderProduct] = self.order_products.filter()

        for order_product in order_products:
            total_discounted_price += order_product.final_price_with_offset()

        return total_discounted_price + delivery_charge

    def calculate_due(self):
        return self.total_price - self.payable_amount

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.serial_number = unique_number_generator(self)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]


class OrderProduct(BaseModelwithUID):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_products"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="this will calculate the final price of the product with discount price",
    )
    discount_price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="we only accept percentage value.",
    )
    quantity = models.PositiveIntegerField(default=0, validators=[MinValueValidator(1)])
    updated_quantity = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(1)],
        help_text="Update the order quantity after returning the quantity",
    )
    delivery_quantity = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return f"Order ID: {self.order.serial_number}, Customer: {self.product.name()}, Total: {self.selling_price}"

    def calculate_updated_price(self):
        return self.updated_quantity * self.selling_price

    def final_price_with_offset(self):
        return (
            self.selling_price * (1 - (self.discount_price / decimal.Decimal(100)))
        ) * self.updated_quantity

    class Meta:
        unique_together = (
            (
                "order",
                "product",
            ),
        )

        ordering = ["-created_at"]


class ReturnOrderProduct(BaseModelwithUID):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True)
    order_product = models.ForeignKey(OrderProduct, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True)
    returned_quantity = models.PositiveIntegerField(
        default=0,
    )
    is_return_by_merchant = models.BooleanField(default=False)
    note = models.CharField(blank=True, max_length=800)
    description = models.TextField(blank=True)
    is_damage = models.BooleanField(
        help_text="If true, this will save to product damage_stock, otherwise it will save to product stock"
    )

    # history
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if self.pk is None:
            if not self.organization:
                self.organization = self.order_product.product.organization
            if not self.order:
                self.order = self.order_product.order
            if not self.product:
                self.product = self.order_product.product
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]


class OrderDelivery(BaseModelwithUID):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="delivery_statuses", blank=True
    )
    status = models.CharField(
        max_length=50,
        default=OrderDeliveryStatus.ORDER_PLACED,
        choices=OrderDeliveryStatus.choices,
    )
    stage = models.CharField(max_length=15, choices=OrderStageChoices.choices)

    # history
    history = HistoricalRecords()

    class Meta:
        unique_together = (
            "order",
            "status",
        )

    def __str__(self):
        return f"Order ID: {self.order.serial_number}, Status: {self.status}"

    def save(self, *args, **kwargs):
        if self.pk is not None and self.stage == OrderStageChoices.CURRENT:
            up_to_status = OrderDeliveryStatus.choices.index(
                (self.status, dict(OrderDeliveryStatus.choices)[self.status])
            )
            status_by_name = [
                choice[0] for choice in OrderDeliveryStatus.choices[:up_to_status]
            ]
            OrderDelivery.objects.filter(order=self.order).exclude(pk=self.pk).update(
                stage=Case(
                    When(
                        status__in=status_by_name,
                        then=Value(OrderStageChoices.COMPLETED),
                    ),
                    default=Value(OrderStageChoices.PENDING),
                )
            )
        super().save(*args, **kwargs)

    """
    In signal (orderio.signals):
    1. we added a instance of TransactionOrganizationUser with amount after creating a instance of Order instance.

    """
