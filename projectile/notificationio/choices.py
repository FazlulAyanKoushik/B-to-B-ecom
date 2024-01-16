from django.db import models


class ActivityActionTypeStatusChoices(models.TextChoices):
    READ = (
        "READ",
        "Read",
    )
    ADDITION = (
        "ADDITION",
        "Addition",
    )
    CHANGE = (
        "CHANGE",
        "Change",
    )
    DELETION = (
        "DELETION",
        "Deletion",
    )
    LOGIN = (
        "LOGIN",
        "Login",
    )
    LOGOUT = (
        "LOGOUT",
        "Logout",
    )


class NotificationEnableStatusChoices(models.TextChoices):
    ON = (
        "ON",
        "On",
    )
    OFF = (
        "OFF",
        "Off",
    )
    OFF_BY_ADMIN = "OFF BY ADMIN", "Off by admin"


class NotificationModelTypeChoices(models.TextChoices):
    USER = "USER", "User"
    ORGANIZATION = "ORGANIZATION", "Organization"
    ORGANIZATION_USER = "ORGANIZATION_USER", "Organization User"
    PRODUCT = "PRODUCT", "Product"
    ORDER = "ORDER", "Order"
    ORDER_DELIVERY = "ORDER_DELIVERY", "Order Delivery"
    CART = "CART", "Cart"
    CART_PRODUCT = "CART_PRODUCT", "Cart Product"
    TRANSACTION = "TRANSACTION", "Transaction"
