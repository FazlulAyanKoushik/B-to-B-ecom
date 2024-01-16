from django.db import models


class OrderDeliveryStatus(models.TextChoices):
    ORDER_PLACED = "ORDER_PLACED", "Order Placed"
    ACCEPTED = "ACCEPTED", "Accepted"
    PROCESSING = "PROCESSING", "Processing"
    PACKAGING = "PACKAGING", "Packaging"
    PARTIAL_DELIVERY = "PARTIAL_DELIVERY", "Partial Delivery"
    WAITING_FOR_DELIVERER = "WAITING_FOR_DELIVERER", "Waiting For Deliverer"
    ON_THE_WAY = "ON_THE_WAY", "On The Way"
    PARTIAL_RETURNED = "PARTIAL_RETURNED", "Partial Returned"
    RETURNED = "RETURNED", "Returned"
    CANCELED = "CANCELED", "Canceled"
    COMPLETED = "COMPLETED", "Completed"


class OrderStageChoices(models.TextChoices):
    PENDING = (
        "PENDING",
        "Pending",
    )
    CURRENT = "CURRENT", "Current"
    COMPLETED = "COMPLETED", "Completed"
