from decimal import Decimal


def get_product_slug(instance):
    return instance.base_product.name


def get_base_product_slug(instance):
    return instance.name


def discount_price_calculator(selling_price, discount_price) -> Decimal:
    return selling_price - (selling_price * (discount_price / Decimal(100)))
