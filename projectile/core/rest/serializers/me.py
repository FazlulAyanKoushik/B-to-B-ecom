from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.models import Q

from rest_framework import serializers
from rest_framework.exceptions import ValidationError, NotFound

from phonenumber_field.serializerfields import PhoneNumberField

from rest_framework.exceptions import APIException
from rest_framework.generics import get_object_or_404

from versatileimagefield.serializers import VersatileImageFieldSerializer

from accountio.choices import OrganizationUserRole
from accountio.models import Organization, OrganizationUser

from threadio.models import Thread, Inbox
from threadio.choices import ThreadKind

from core.rest.serializers.auth import GlobalUserSlimSerializer
from core.rest.serializers.notifications import (
    PublicNotificationOrderDeliverySerializer,
    PublicNotificationOrderSerializer,
    PublicNotificationUserSerializer,
    PublicNotificationTransactionSerializer,
)

from notificationio.models import (
    NotificationModelConnector,
    Notification,
    NotificationUserReceiver,
)

from weapi.rest.serializers.orders import (
    PrivateUserSerializer,
)
from weapi.rest.serializers.organizations import PrivateOrganizationSerializer
from weapi.rest.serializers.products import PrivateProductSerializer
from weapi.rest.serializers.users import (
    PrivateOrganizationUserSerializer,
)

from common.serializers import BaseModelSerializer

User = get_user_model()


class PublicOrganizationUserSerializer(serializers.ModelSerializer):
    user = GlobalUserSlimSerializer(read_only=True)

    class Meta:
        model = OrganizationUser
        fields = ["uid", "user", "role", "status", "created_at", "updated_at"]
        read_only_fields = ["uid", "user", "created_at", "updated_at"]


class PublicOrganizationPostSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    role = serializers.ChoiceField(
        choices=OrganizationUserRole.choices,
    )
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    email = serializers.EmailField(allow_blank=True)
    phone = PhoneNumberField()
    password = serializers.CharField(max_length=255, write_only=True)

    def create(self, validated_data):
        with transaction.atomic():
            organization = validated_data.get("user").get_organization()
            phone = validated_data.get("phone")
            user, _ = User.objects.get_or_create(
                phone=phone,
                defaults={
                    "first_name": validated_data.get("first_name", ""),
                    "last_name": validated_data.get("last_name", ""),
                    "phone": phone,
                    "password": make_password(validated_data.get("password")),
                    "email": validated_data.get("email"),
                },
            )
            role = validated_data.get("role")
            organization_set = OrganizationUser.objects.filter(
                organization=organization, user=user
            )
            if organization_set.exists():
                raise ValidationError(
                    {
                        "detail": "This user is already added to your current organization."
                    }
                )
            else:
                OrganizationUser.objects.create(
                    organization=organization, user=user, role=role, is_default=True
                )

        return validated_data


class PrivateMeSerializer(serializers.ModelSerializer):
    image = VersatileImageFieldSerializer(
        required=False,
        sizes=[
            ("original", "url"),
            ("at256", "crop__256x256"),
            ("at512", "crop__512x512"),
        ],
    )
    discount_offset = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "slug",
            "phone",
            "image",
            "email",
            "discount_offset",
        ]

        read_only_fields = ["slug", "phone"]


class PrivateNotificationModelConnectorSerializer(serializers.ModelSerializer):
    user = PrivateUserSerializer(allow_null=True, read_only=True)
    organization = PrivateOrganizationSerializer(allow_null=True, read_only=True)
    organization_user = PrivateOrganizationUserSerializer(
        allow_null=True, read_only=True
    )
    product = PrivateProductSerializer(allow_null=True, read_only=True)
    order = PublicNotificationOrderSerializer(
        allow_null=True, read_only=True
    )  # eager loading with order products
    order_delivery = PublicNotificationOrderDeliverySerializer(
        allow_null=True, read_only=True
    )
    transaction = PublicNotificationTransactionSerializer(
        allow_null=True, read_only=True
    )

    class Meta:
        model = NotificationModelConnector
        fields = [
            "user",
            "organization",
            "organization_user",
            "product",
            "order",
            "order_delivery",
            "transaction",
            "created_at",
        ]
        read_only_fields = fields


class PrivateNotificationListSerializer(serializers.ModelSerializer):
    is_read = serializers.SerializerMethodField()
    created_by = PublicNotificationUserSerializer(read_only=True)
    current_model = PrivateNotificationModelConnectorSerializer(
        read_only=True, source="notificationmodelconnector"
    )

    class Meta:
        model = Notification
        fields = [
            "uid",
            "changed_data",
            "created_by",
            "is_success",
            "message",
            "action_type",
            "model_type",
            "is_read",
            "current_model",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_is_read(self, instance: Notification):
        user: User = self.context["request"].user

        # notification user receiver
        try:
            notification_user_receiver: NotificationUserReceiver = (
                instance.notificationuserreceiver_set.get(user=user)
            )
        except NotificationUserReceiver.DoesNotExist:
            raise NotFound("Notification Receiver cannot found.")

        return notification_user_receiver.is_read


class BaseUserSerializer(BaseModelSerializer):
    name = serializers.CharField(max_length=100, source="get_name")

    class Meta:
        model = User
        fields = [
            "uid",
            "first_name",
            "last_name",
            "name",
            "date_joined",
            "last_login",
            "country",
            "model",
        ]


class UserSlimSerializer(BaseUserSerializer):
    avatar = VersatileImageFieldSerializer(
        sizes=[
            ("original", "url"),
            ("at256", "thumbnail__256x256"),
            ("at512", "thumbnail__512x512"),
        ],
        required=False,
    )

    class Meta(BaseUserSerializer.Meta):
        fields = [
            "uid",
            "first_name",
            "last_name",
            "name",
            "avatar",
        ]
        read_only_fields = ("__all__",)


class LastThreadSerializer(serializers.ModelSerializer):
    author = UserSlimSerializer(read_only=True)

    class Meta:
        model = Thread
        fields = [
            "uid",
            "content",
            "author",
            "created_at",
            "is_send_by_customer",
            "is_read",
        ]

        read_only_fields = [
            "is_send_by_customer",
            "is_read",
        ]


class OrganizationDetailSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "uid",
            "name",
            "slug",
            "domain",
        ]


class PrivateThreadReplySerializer(serializers.ModelSerializer):
    author = UserSlimSerializer(read_only=True)
    organization = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Thread
        fields = [
            "uid",
            "content",
            "author",
            "organization",
            "created_at",
            "is_send_by_customer",
        ]

        read_only_fields = [
            "is_send_by_customer",
        ]

    def get_organization(self, object):
        request_user = self.context.get("request").user
        organization = request_user.get_organization()

        return OrganizationDetailSerilizer(organization).data

    def create(self, validated_data):
        request_user = self.context["request"].user
        parent_uid = self.context["request"].parser_context["kwargs"].get("uid")
        parent = get_object_or_404(Thread.objects.filter(), uid=parent_uid)
        thread = Thread.objects.create(
            parent=parent,
            author=request_user,
            kind=ThreadKind.CHILD,
            is_send_by_customer=True,
            is_read=False,
            **validated_data,
        )
        # Update unread_count for the parent thread's inbox

        Inbox.objects.filter(thread=parent).exclude(user=request_user).update(
            unread_count=1
        )

        return thread


class PrivateThreadListSerializer(serializers.ModelSerializer):
    author = UserSlimSerializer(read_only=True)
    last_message = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Thread
        fields = [
            "uid",
            "content",
            "author",
            "is_send_by_customer",
            "last_message",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["is_read", "is_send_by_customer"]

    # Getting the last message
    def get_last_message(self, object):
        last_message = (
            Thread.objects.select_related("author")
            .filter(Q(parent=object) | Q(pk=object.pk))
            .order_by("-created_at")
            .first()
        )
        return LastThreadSerializer(last_message).data

    def create(self, validated_data):
        request_user = self.context["request"].user
        organization = request_user.get_organization()
        threads = Inbox.objects.filter(user=request_user).values_list(
            "thread", flat=True
        )
        inbox = Inbox.objects.filter(
            user=request_user, organization=organization
        ).first()

        if inbox:
            thread = Thread.objects.create(
                parent=inbox.thread,
                author=request_user,
                kind=ThreadKind.CHILD,
                is_send_by_customer=True,
                **validated_data,
            )
            inbox.unread_count += 1
            inbox.save()
            return thread

        thread = Thread.objects.create(
            author=request_user,
            kind=ThreadKind.PARENT,
            is_send_by_customer=True,
            **validated_data,
        )
        Inbox.objects.create(
            thread=thread,
            user=request_user,
            organization=organization,
        )
        Inbox.objects.filter(thread=thread).exclude(user=request_user).update(
            unread_count=1
        )
        return thread
