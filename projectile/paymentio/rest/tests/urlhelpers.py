from django.urls import reverse


def payment_method_url():
    return reverse("payments-list")
