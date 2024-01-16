import logging

from django.db.models import Max, Q

from rest_framework import filters
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    get_object_or_404,
    RetrieveUpdateAPIView,
    UpdateAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

from accountio.choices import OrganizationUserRole
from accountio.choices import OrganizationUserStatus
from accountio.models import OrganizationUser, Organization
from accountio.utils import get_subdomain

from core.rest.serializers.me import (
    PublicOrganizationUserSerializer,
    PublicOrganizationPostSerializer,
    PrivateMeSerializer,
    PrivateNotificationListSerializer,
    PrivateThreadListSerializer,
    PrivateThreadReplySerializer,
)
from core.rest.serializers.notifications import PublicNotificationCountSerializer

from notificationio.models import Notification, NotificationUserReceiver

from threadio.models import Thread, Inbox
from threadio.choices import ThreadKind

from weapi.rest import permissions

logger = logging.getLogger(__name__)


statuses = [
    OrganizationUserStatus.INVITED,
    OrganizationUserStatus.PENDING,
    OrganizationUserStatus.ACTIVE,
    OrganizationUserStatus.HIDDEN,
    OrganizationUserStatus.SUSPEND,
]


@extend_schema(
    parameters=[
        OpenApiParameter(
            "role", OpenApiTypes.STR, description="Ex: ADMIN, STAFF,OWNER, CUSTOMER"
        ),
    ],
)
class PrivateOrganizationUserList(ListCreateAPIView):
    queryset = OrganizationUser.objects.select_related("user").filter(
        status__in=statuses
    )
    permission_classes = [permissions.IsOrganizationStaff]
    filter_backends = [filters.SearchFilter]
    ordering = ["-role"]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__phone",
        "user__email",
    ]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return PublicOrganizationUserSerializer
        else:
            return PublicOrganizationPostSerializer

    def get_queryset(self):
        organization = self.request.user.get_organization()

        organization_users = (
            self.queryset.select_related("user")
            .filter(organization=organization)
            .filter(
                role__in=[
                    OrganizationUserRole.ADMIN,
                    OrganizationUserRole.OWNER,
                    OrganizationUserRole.STAFF,
                    OrganizationUserRole.MANAGER,
                ]
            )
            .order_by("created_at")
        )

        role = self.request.query_params.get("role", "")
        if role:
            organization_users = organization_users.filter(role=role)
        return organization_users

    def perform_create(self, serializer):
        role = serializer.validated_data.get("role", None)
        if (
            role
            and role == "owner"
            and serializer.validated_data.get("user").get_my_organization_role().lower()
            != "owner"
        ):
            raise ValidationError("Unauthorized access", code=422)
        if (
            role
            and (role == "admin" or role == "staff")
            and serializer.validated_data.get("user").get_my_organization_role().lower()
            == "staff"
        ):
            raise ValidationError("Unauthorized access", code=422)
        serializer.save()
        return serializer


class PrivateOrganizationUserDetail(RetrieveUpdateDestroyAPIView):
    queryset = OrganizationUser.objects.select_related("user").filter(
        status__in=statuses
    )
    serializer_class = PublicOrganizationUserSerializer
    permission_classes = [permissions.IsOrganizationStaff]

    def get_object(self):
        uid = self.kwargs.get("uid", None)
        return get_object_or_404(OrganizationUser.objects.filter(), uid=uid)


class PrivateMeDetail(RetrieveUpdateAPIView):
    permission_classes = [
        permissions.IsOrganizationCustomer | permissions.IsOrganizationStaff
    ]
    serializer_class = PrivateMeSerializer

    def get_object(self):
        organization = get_subdomain(self.request)
        self.request.user.discount_offset = get_object_or_404(
            self.request.user.organizationuser_set.filter(), organization=organization
        ).discount_offset

        return self.request.user


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Organization user can change their default organization.",
            request_only=False,
            response_only=False,
        ),
    ]
)
class PrivateOrganizationDefaultDetail(UpdateAPIView):
    http_method_names = ("patch",)
    serializer_class = PublicOrganizationUserSerializer
    organization_user: OrganizationUser = None

    def check_permissions(self, request):
        organization_slug = self.kwargs.get("organization_slug")
        try:
            organization = Organization.objects.get(domain=organization_slug)
        except Organization.DoesNotExist:
            self.permission_denied(
                request,
                message="You do not have permission to do this action",
            )
            return

        try:
            self.organization_user = OrganizationUser.objects.filter(
                organization=organization
            ).get(user=self.request.user)
        except OrganizationUser.DoesNotExist:
            self.permission_denied(
                request,
                message="You do not have permission to do this action",
            )
            return

    def update(self, request, *args, **kwargs):
        if self.organization_user is None:
            organization_slug = self.kwargs.get("organization_slug")

            organization: Organization = get_object_or_404(
                Organization.objects.filter(), domain=organization_slug
            )

            self.organization_user = OrganizationUser.objects.filter(
                organization=organization
            ).get(user=self.request.user)

        target_organization_user: OrganizationUser = self.organization_user
        target_organization_user.is_default = True
        target_organization_user.save_dirty_fields()

        return Response(status=200)


@extend_schema(
    parameters=[
        OpenApiParameter(
            "status",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="Values: read, unread, all",
        ),
    ],
)
class PrivateNotificationList(ListAPIView):
    serializer_class = PrivateNotificationListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        notification_user_receivers = NotificationUserReceiver.objects.select_related(
            "notification"
        ).filter(user=self.request.user)

        # filter by status
        seen_status = self.request.query_params.get("status", "")
        if seen_status == "read":
            notification_user_receivers = notification_user_receivers.filter(
                is_read=True
            )
        elif seen_status == "unread":
            notification_user_receivers = notification_user_receivers.filter(
                is_read=False
            )

        # get the all id of notification
        notification_ids = notification_user_receivers.values_list(
            "notification", flat=True
        )
        organization: Organization = get_subdomain(self.request)
        # Fetch the corresponding Notification objects
        notifications = (
            Notification.objects.prefetch_related(
                "notificationuserreceiver_set", "notificationmodelconnector"
            )
            .filter(pk__in=notification_ids, organization=organization)
            .order_by("-created_at")
        )

        return notifications


class PrivateNotificationDetail(UpdateAPIView):
    serializer_class = PrivateNotificationListSerializer
    http_method_names = ["patch"]
    permission_classes = [IsAuthenticated]

    def get_object(self) -> Notification:
        # get organization from the x-domain
        organization = get_subdomain(self.request)

        # get the object
        return get_object_or_404(
            Notification.objects.select_related("notificationmodelconnector").filter(
                notificationuserreceiver__user=self.request.user,
                organization=organization,
            ),
            uid=self.kwargs.get("uid"),
        )

    def perform_update(self, serializer):
        self.get_object().notificationuserreceiver_set.filter(
            user=self.request.user
        ).update(is_read=True)


class PrivateNotificationSeenAllDetail(UpdateAPIView):
    serializer_class = PrivateNotificationListSerializer
    http_method_names = ["put"]
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        # get organization from x-domain
        organization = get_subdomain(request)

        # updating all unread notification to read to a organization
        NotificationUserReceiver.objects.filter(
            is_read=False,
            user=request.user,
            notification__organization=organization,
        ).update(is_read=True)

        return Response(status=200)


class PrivateNotificationCountDetail(RetrieveAPIView):
    serializer_class = PublicNotificationCountSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        organization = get_subdomain(self.request)

        notification_user_receivers = NotificationUserReceiver.objects.select_related(
            "notification"
        ).filter(
            user=self.request.user,
            notification__organization=organization,
        )

        return {
            "read_count": notification_user_receivers.filter(is_read=True).count(),
            "unread_count": notification_user_receivers.filter(is_read=False).count(),
        }


class PrivateThreadList(ListCreateAPIView):
    # queryset = Thread.objects.filter()
    permission_classes = [permissions.IsOrganizationCustomer]
    serializer_class = PrivateThreadListSerializer

    def get_queryset(self):
        user = self.request.user
        organization = user.get_organization()
        return (
            Thread.objects.select_related("author")
            .filter(
                inbox__user=user,
                inbox__organization=organization,
                kind=ThreadKind.PARENT,
            )
            .annotate(last_message_time=Max("replies__created_at"))
            .order_by("-last_message_time", "-created_at")
        )


class PrivateThreadReplyList(ListCreateAPIView):
    serializer_class = PrivateThreadReplySerializer
    permission_classes = [permissions.IsOrganizationCustomer]

    def get_queryset(self):
        uid = self.kwargs.get("uid")
        user = self.request.user
        organization = user.get_organization()
        parent = get_object_or_404(
            Thread.objects.select_related("author").filter(),
            uid=uid,
        )

        if Inbox.objects.filter(
            thread=parent, user=self.request.user, organization=organization
        ).exists():
            inbox = Inbox.objects.filter(
                thread=parent, user=self.request.user, organization=organization
            ).first()
            """
            in this try block, we attempt to retrieve the Inbox instance
            for the current user and the parent thread. If it exists and its
            unread_count is greater than 0.
            """
            if inbox and inbox.unread_count > 0:
                inbox.mark_as_read()

        else:
            raise ValidationError("your inbox is not created yet")

        return (
            Thread.objects.select_related("author")
            .filter(Q(parent=parent) | Q(pk=parent.pk))
            .order_by("created_at")
            .exclude(content="")
        )
