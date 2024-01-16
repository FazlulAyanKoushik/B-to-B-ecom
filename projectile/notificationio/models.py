from django.db import models

from core.utils import BaseModelwithUID

from notificationio.choices import (
    ActivityActionTypeStatusChoices,
    NotificationEnableStatusChoices,
    NotificationModelTypeChoices,
)


class NotificationUserPreference(BaseModelwithUID):
    user = models.ForeignKey("core.User", on_delete=models.CASCADE)
    organization = models.ForeignKey(
        "accountio.Organization", models.CASCADE, null=True, blank=True
    )
    enable_user_notification = models.CharField(
        max_length=15,
        choices=NotificationEnableStatusChoices.choices,
        default=NotificationEnableStatusChoices.ON,
    )
    enable_product_notification = models.CharField(
        max_length=15,
        choices=NotificationEnableStatusChoices.choices,
        default=NotificationEnableStatusChoices.ON,
    )
    enable_order_notification = models.CharField(
        max_length=15,
        choices=NotificationEnableStatusChoices.choices,
        default=NotificationEnableStatusChoices.ON,
    )
    enable_order_delivery_notification = models.CharField(
        max_length=15,
        choices=NotificationEnableStatusChoices.choices,
        default=NotificationEnableStatusChoices.ON,
    )
    enable_organization_notification = models.CharField(
        max_length=15,
        choices=NotificationEnableStatusChoices.choices,
        default=NotificationEnableStatusChoices.ON,
    )
    enable_organization_user_notification = models.CharField(
        max_length=15,
        choices=NotificationEnableStatusChoices.choices,
        default=NotificationEnableStatusChoices.ON,
    )
    enable_cart_notification = models.CharField(
        max_length=15,
        choices=NotificationEnableStatusChoices.choices,
        default=NotificationEnableStatusChoices.ON,
    )
    enable_cart_product_notification = models.CharField(
        max_length=15,
        choices=NotificationEnableStatusChoices.choices,
        default=NotificationEnableStatusChoices.ON,
    )
    enable_transaction_notification = models.CharField(
        max_length=15,
        choices=NotificationEnableStatusChoices.choices,
        default=NotificationEnableStatusChoices.ON,
    )

    class Meta:
        unique_together = ("user", "organization")


class Notification(BaseModelwithUID):
    created_by = models.ForeignKey("core.User", on_delete=models.CASCADE)
    organization = models.ForeignKey(
        "accountio.Organization", models.CASCADE, null=True, blank=True
    )
    changed_data = models.JSONField(
        default=dict, help_text="Will save the previous data using serializer"
    )
    is_success = models.BooleanField(
        help_text="If response status is below than 400, it will save as success response"
    )
    message = models.CharField(
        max_length=500, blank=True, help_text="Message for notification if needed"
    )
    action_type = models.CharField(
        choices=ActivityActionTypeStatusChoices.choices,
        max_length=10,
        help_text="Requested method",
    )
    model_type = models.CharField(
        max_length=30, choices=NotificationModelTypeChoices.choices
    )

    class Meta:
        ordering = ("-created_at",)


class NotificationModelConnector(BaseModelwithUID):
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE)
    # connector models
    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, null=True, blank=True
    )
    organization = models.ForeignKey(
        "accountio.Organization", on_delete=models.CASCADE, null=True, blank=True
    )
    organization_user = models.ForeignKey(
        "accountio.OrganizationUser", on_delete=models.CASCADE, null=True, blank=True
    )
    product = models.ForeignKey(
        "catalogio.Product", on_delete=models.CASCADE, null=True, blank=True
    )
    order = models.ForeignKey(
        "orderio.Order", on_delete=models.CASCADE, null=True, blank=True
    )
    order_delivery = models.ForeignKey(
        "orderio.OrderDelivery", on_delete=models.CASCADE, null=True, blank=True
    )
    transaction = models.ForeignKey(
        "accountio.TransactionOrganizationUser",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )


class NotificationUserReceiver(BaseModelwithUID):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    user = models.ForeignKey("core.User", on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    class Meta:
        unique_together = ("notification", "user")
