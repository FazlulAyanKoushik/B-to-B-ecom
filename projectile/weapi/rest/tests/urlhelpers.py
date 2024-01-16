from django.urls import reverse


def organization_list_url():
    return reverse("organization-list")


def organization_detail_url():
    return reverse("organization-detail")


def product_categories_list_url():
    return reverse("organization-product-category-list")


def organization_customer_list_url():
    return reverse("organization-customer-list")


def organization_customer_detail_url(uid):
    return reverse("organization-customer-detail", args=[uid])


def customer_delivery_charge_detail(uid):
    return reverse("customer-order-delivery-charge", args=[uid])


def organization_product_category_list_url():
    return reverse("organization-product-category-list")


def organization_address_url():
    return reverse("organization-address-list")


def organization_address_detail_url(uuid):
    return reverse("organization-address-detail", args=[uuid])


def organization_user_list_url():
    return reverse("organization-user-list")


def organization_user_detail_url(uid):
    return reverse("organization-user-detail", args=[uid])


def organization_default_detail_url(uid):
    return reverse("me-organization-set-default", args=[uid])


def organization_info_detail_url():
    return reverse("organization-info-detail")


def brand_list_url():
    return reverse("brand-list")


def category_list_url():
    return reverse("category-list")


def ingredient_list_url():
    return reverse("ingredient-list")


def medicine_physical_state_list_url():
    return reverse("medicine-physical-state-list")


def route_of_administration_list_url():
    return reverse("route-of-administration-list")


def product_list_url():
    return reverse("products-list")


def product_detail_url(uid):
    return reverse("product-detail", args=[uid])


def create_customer_address_url():
    return reverse("customer-address-list")


def cart_products_list_url():
    return reverse("cart_product-list")


def cart_products_remove_url(product_slug):
    return reverse("cart_product-remove", args=[product_slug])


def create_order_list_url():
    return reverse("customer-order-list")


def customer_order_detail_url(uid):
    return reverse("customer-order-detail", args=[uid])


def customer_address_list_url():
    return reverse("customer-address-list")


def customer_address_detail_url(uid):
    return reverse("customer-address-detail", args=[uid])


def private_customer_order_count_url(uid):
    return reverse("organization-customer-order-analytics", args=[uid])


def private_customer_order_count_by_month_of_a_year_url(uid, year):
    return reverse("organization-customer-order-count-by-month-of-a-year", args=[uid, year])


def search_base_product_url():
    return reverse("search-base.product")


def dashboard_list_url():
    return reverse("dashboard-list")


def private_orders_list_url():
    return reverse("orders-list")


def private_orders_detail_url(uid):
    return reverse("order-details", args=[uid])


def manufacturer_list_url():
    return reverse("manufacturer-list")


def dosage_form_list_url():
    return reverse("dosage-form-list")


def tag_list_url():
    return reverse("tag-list")


def tag_detail_url(uid):
    return reverse("tag-detail", args=[uid])


def search_product_url():
    return reverse("search-product")


def bulk_discount_update_url():
    return reverse("product-bulk-discount-by-filter")


def product_out_of_stock_url():
    return reverse("product-out-of-stock-list")


def product_bulk_download_url():
    return reverse("product-bulk-download")


def product_bulk_update_url():
    return reverse("product-bulk-upload")

def private_customer_order_transactions():
    return reverse("customer-transactions")

def get_user():
    return reverse("me-detail")
