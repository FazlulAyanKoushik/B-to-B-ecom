from django.urls import reverse


def product_list_url():
    return reverse("global-product-list")


def product_detail_url(slug):
    return reverse("global-product-detail", args=[slug])