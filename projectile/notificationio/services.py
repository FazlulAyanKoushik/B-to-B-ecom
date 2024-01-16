from decimal import Decimal
import logging
from typing import List

from django.db import transaction

from rest_framework.exceptions import ValidationError

from rest_framework.request import Request

from accountio.choices import OrganizationUserRole
from accountio.models import Organization, OrganizationUser
from accountio.utils import get_subdomain

from core.models import User

from notificationio.choices import (
    ActivityActionTypeStatusChoices,
    NotificationEnableStatusChoices,
    NotificationModelTypeChoices,
)

from notificationio.models import (
    NotificationUserPreference,
    Notification,
    NotificationUserReceiver,
    NotificationModelConnector,
)

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, request: Request, organization: Organization = None):
        self._request = request
        self._organization = organization

        if organization is None:
            self._organization = get_subdomain(request)

    def _get_current_user(self) -> User | None:
        return self._request.user if self._request.user.is_authenticated else None

    @staticmethod
    def action_type_mapper():
        return {
            "GET": ActivityActionTypeStatusChoices.READ,
            "POST": ActivityActionTypeStatusChoices.ADDITION,
            "PUT": ActivityActionTypeStatusChoices.CHANGE,
            "PATCH": ActivityActionTypeStatusChoices.CHANGE,
            "DELETE": ActivityActionTypeStatusChoices.DELETION,
        }

    def _model_type_mapper(self):
        return {
            "User": NotificationModelTypeChoices.USER,
            "Organization": NotificationModelTypeChoices.ORGANIZATION,
            "OrganizationUser": NotificationModelTypeChoices.ORGANIZATION_USER,
            "Product": NotificationModelTypeChoices.PRODUCT,
            "Order": NotificationModelTypeChoices.ORDER,
            "OrderDelivery": NotificationModelTypeChoices.ORDER_DELIVERY,
            "TransactionOrganizationUser": NotificationModelTypeChoices.TRANSACTION,
        }

    def _get_model_type(self, instance) -> NotificationModelTypeChoices:
        model = instance.__class__.__name__
        return self._model_type_mapper().get(model)

    def _check_if_user_has_model_permission_mapper(self):
        return {
            "User": "enable_user_notification",
            "Product": "enable_product_notification",
            "Order": "enable_order_notification",
            "OrderDelivery": "enable_order_delivery_notification",
            "Organization": "enable_organization_notification",
            "OrganizationUser": "enable_organization_user_notification",
            "TransactionOrganizationUser": "enable_transaction_notification",
        }

    def _get_if_user_has_model_permission(self, instance) -> (str, str):
        model_name = instance.__class__.__name__
        model_preference_name = self._check_if_user_has_model_permission_mapper().get(
            model_name
        )
        return model_preference_name, model_name

    def set_user_preference(
        self,
        user: User,
        enable_user_notification: NotificationEnableStatusChoices = NotificationEnableStatusChoices.ON,
        enable_product_notification: NotificationEnableStatusChoices = NotificationEnableStatusChoices.ON,
        enable_order_notification: NotificationEnableStatusChoices = NotificationEnableStatusChoices.ON,
        enable_order_delivery_notification: NotificationEnableStatusChoices = NotificationEnableStatusChoices.ON,
        enable_organization_notification: NotificationEnableStatusChoices = NotificationEnableStatusChoices.ON,
        enable_organization_user_notification: NotificationEnableStatusChoices = NotificationEnableStatusChoices.ON,
        enable_cart_notification: NotificationEnableStatusChoices = NotificationEnableStatusChoices.ON,
        enable_cart_product_notification: NotificationEnableStatusChoices = NotificationEnableStatusChoices.ON,
        enable_transaction_notification: NotificationEnableStatusChoices = NotificationEnableStatusChoices.ON,
    ) -> NotificationUserPreference:
        return NotificationUserPreference.objects.create(
            user=user,
            organization=self._organization,
            enable_user_notification=enable_user_notification,
            enable_product_notification=enable_product_notification,
            enable_order_notification=enable_order_notification,
            enable_order_delivery_notification=enable_order_delivery_notification,
            enable_organization_notification=enable_organization_notification,
            enable_organization_user_notification=enable_organization_user_notification,
            enable_cart_notification=enable_cart_notification,
            enable_cart_product_notification=enable_cart_product_notification,
            enable_transaction_notification=enable_transaction_notification,
        )

    def _get_action_type(self) -> str:
        return self.action_type_mapper().get(f"{self._request.method.upper()}")

    def _check_if_user_has_permission(self, user: User, preference_enable: str) -> bool:
        try:
            preference_user_data: dict = (
                self._get_notification_user_preference(user=user)
            ).__dict__
            if preference_user_data[preference_enable] == "ON":
                return True
            return False
        except NotificationUserPreference.DoesNotExist:
            self.set_user_preference(user=user)
            return True

    def _get_notification_user_preference(
        self, user: User
    ) -> NotificationUserPreference:
        return NotificationUserPreference.objects.get(
            organization=self._organization, user=user
        )

    def convert_decimal_to_string(self, data):
        for key, value in data.items():
            if isinstance(value, dict):
                self.convert_decimal_to_string(value)
            elif isinstance(value, Decimal):
                data[key] = str(value)
        return data

    def create_notification(
        self,
        saved_or_updated_instance,
        status_code: int,
        message: str = "",
        previous_data=None,
        action_type: ActivityActionTypeStatusChoices = None,
    ) -> Notification:
        if previous_data is None:
            previous_data = {}
        # if previous_data == {} and self._request.method in ["PUT", "PATCH"]:
        #     raise ValidationError(
        #         {"detail": "Previous data cannot be null while PUT or PATCH method."}
        #     )

        if previous_data:
            previous_data = self.convert_decimal_to_string(previous_data)

        return Notification.objects.create(
            created_by=self._request.user,
            organization=self._organization,
            changed_data=previous_data,
            is_success=True if status_code < 300 else False,
            message=message,
            action_type=action_type if action_type else self._get_action_type(),
            model_type=self._get_model_type(saved_or_updated_instance),
        )

    def create_notification_model_connector(
        self, notification: Notification, saved_or_updated_instance
    ) -> NotificationModelConnector:
        notification_model_connector = NotificationModelConnector()
        notification_model_connector.notification = notification
        if notification.model_type == NotificationModelTypeChoices.USER:
            notification_model_connector.user = saved_or_updated_instance
        elif notification.model_type == NotificationModelTypeChoices.PRODUCT:
            notification_model_connector.product = saved_or_updated_instance
        elif notification.model_type == NotificationModelTypeChoices.ORDER:
            notification_model_connector.order = saved_or_updated_instance
        elif notification.model_type == NotificationModelTypeChoices.ORDER_DELIVERY:
            notification_model_connector.order_delivery = saved_or_updated_instance
        elif notification.model_type == NotificationModelTypeChoices.ORGANIZATION:
            notification_model_connector.organization = saved_or_updated_instance
        elif notification.model_type == NotificationModelTypeChoices.ORGANIZATION_USER:
            notification_model_connector.organization_user = saved_or_updated_instance
        elif notification.model_type == NotificationModelTypeChoices.TRANSACTION:
            notification_model_connector.transaction = saved_or_updated_instance

        else:
            raise ValidationError(
                {"detail": "Cannot set notification current model instance value."}
            )

        return notification_model_connector.save()

    def create_notification_user_receiver(
        self, notification: Notification, user: User, is_read=False
    ) -> NotificationUserReceiver:
        instance, _ = NotificationUserReceiver.objects.get_or_create(
            notification=notification, user=user, defaults={"is_read": is_read}
        )
        return instance

    def connect_notification_with_users(
        self,
        notification: Notification,
        saved_or_updated_instance,
    ):
        # get all organization users
        organization_users = (
            OrganizationUser.objects.select_related("organization", "user")
            .filter(organization=self._organization)
            .exclude(role__in=[OrganizationUserRole.CUSTOMER])
        )

        # check all organization users have model permission or not
        for organization_user in organization_users:
            # get the preference specific enable
            (
                enable_model_notification,
                model_name,
            ) = self._get_if_user_has_model_permission(saved_or_updated_instance)

            # check the permission
            has_permission = self._check_if_user_has_permission(
                user=organization_user.user, preference_enable=enable_model_notification
            )

            # save the data to the organization
            if has_permission:
                self.create_notification_user_receiver(
                    notification=notification, user=organization_user.user
                )

    def create_notification_with_sending_notification_to_organization_users(
        self,
        saved_or_updated_instance=None,
        message: str = "",
        status_code: int = 200,
        previous_data=None,
        action_type: ActivityActionTypeStatusChoices = None,
    ) -> Notification:
        if previous_data is None:
            previous_data = {}
        with transaction.atomic():
            notification: Notification = self.create_notification(
                saved_or_updated_instance=saved_or_updated_instance,
                status_code=status_code,
                message=message,
                previous_data=previous_data,
                action_type=action_type,
            )
            self.create_notification_model_connector(
                notification=notification,
                saved_or_updated_instance=saved_or_updated_instance,
            )
            self.connect_notification_with_users(
                notification=notification,
                saved_or_updated_instance=saved_or_updated_instance,
            )
        return notification

    def send_notification_to_custom_users(
        self, notification: Notification, user_ids: List[int]
    ):
        for user_id in user_ids:
            user = User.objects.get(id=user_id)
            self.create_notification_user_receiver(notification=notification, user=user)
