from django.core.validators import MinValueValidator

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from versatileimagefield.serializers import VersatileImageFieldSerializer

from accountio.utils import get_subdomain
from catalogio.choices import ProductBoxType

from catalogio.models import Product

from orderio.models import (
    Cart,
    CartProduct,
)

from weapi.rest.serializers.basic import PrivateBasicIngredientSerializer


class PrivateCartProductDetailSerializer(serializers.Serializer):
    slug = serializers.SlugField(read_only=True)
    name = serializers.CharField(read_only=True)
    selling_price = serializers.DecimalField(
        decimal_places=2, max_digits=10, default=0, read_only=True
    )


class PrivateCartProductSerializer(serializers.Serializer):
    slug = serializers.SlugField(
        read_only=True,
        source="product.slug",
    )
    name = serializers.CharField(
        read_only=True,
        source="product.base_product.name",
    )
    selling_price = serializers.DecimalField(
        read_only=True,
        max_digits=10,
        decimal_places=2,
        source="product.selling_price",
    )
    total_discount = serializers.DecimalField(
        read_only=True,
        max_digits=10,
        decimal_places=2,
        source="product.total_discount",
        help_text="Total customer offset and product individual discount.",
    )
    final_price_with_offset = serializers.DecimalField(
        read_only=True,
        max_digits=10,
        decimal_places=2,
        source="product.final_price_with_offset",
        help_text="Product price with customer offset and product discount",
    )
    discount_price = serializers.DecimalField(
        read_only=True,
        max_digits=10,
        decimal_places=2,
        source="product.discount_price",
        help_text="Product discount(product only) price",
    )
    total_price = serializers.DecimalField(
        read_only=True,
        max_digits=10,
        decimal_places=2,
        help_text="Total price (product and customer offset discounted) with quantity",
    )

    active_ingredients = PrivateBasicIngredientSerializer(
        many=True,
        source="product.base_product.active_ingredients",
    )
    dosage_form = serializers.CharField(
        read_only=True,
        source="product.base_product.dosage_form",
    )
    manufacturer = serializers.CharField(
        read_only=True,
        source="product.base_product.manufacturer.name",
    )
    box_type = serializers.ChoiceField(
        choices=ProductBoxType.choices,
        source="product.box_type",
        read_only=True,
    )
    quantity = serializers.IntegerField(min_value=0, read_only=True)
    unit = serializers.CharField(
        read_only=True,
        source="product.base_product.unit",
    )
    strength = serializers.CharField(
        read_only=True, source="product.base_product.strength"
    )

    primary_image = VersatileImageFieldSerializer(
        sizes=[
            ("original", "url"),
            ("at256", "crop__256x256"),
            ("at512", "crop__512x512"),
        ],
        read_only=True,
        source="product.primary_image",
    )

    def get_active_ingredients(self, instance):
        return [
            dosage_form.name
            for dosage_form in instance.product.base_product.active_ingredients.all()
        ]


class PrivateCartsSerializer(serializers.Serializer):
    uid = serializers.UUIDField(read_only=True)
    discount_offset = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )
    total_price = serializers.DecimalField(
        read_only=True, decimal_places=2, max_digits=10
    )
    products = PrivateCartProductSerializer(many=True, read_only=True)

    product = serializers.SlugRelatedField(
        queryset=Product.objects.get_status_active(),
        slug_field="slug",
        write_only=True,
    )
    quantity = serializers.IntegerField(
        validators=[MinValueValidator(1)], write_only=True
    )
    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate(self, attrs):
        organization = get_subdomain(self.context["request"])
        product = attrs.get(
            "product",
        )
        quantity = attrs.get(
            "quantity",
        )

        if product.organization != organization:
            raise ValidationError(
                {
                    "product": f"This product is not {organization.name} organization's product"
                }
            )
        if product.stock < quantity:
            raise ValidationError(
                {"quantity": f"Insufficient stock for {product.base_product.name}"}
            )
        return attrs

    def create(self, validated_data):
        customer = validated_data.get("customer", None)
        quantity = validated_data.get("quantity", None)
        product = validated_data.get("product", None)
        organization = get_subdomain(self.context["request"])

        cart, _ = (
            Cart.objects.prefetch_related("products__product__base_product")
            .select_related("organization")
            .order_by("products__created_at")
            .get_or_create(
                customer=customer,
                organization=organization,
                defaults={"organization": organization},
            )
        )
        cart_product, _ = CartProduct.objects.update_or_create(
            cart=cart, product=product, defaults={"quantity": quantity}
        )
        return validated_data
