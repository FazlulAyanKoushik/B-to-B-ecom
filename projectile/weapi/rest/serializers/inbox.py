from django.db.models import Q

from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from accountio.models import OrganizationUser
from accountio.choices import OrganizationUserRole

from core.rest.serializers.me import (
    UserSlimSerializer,
    LastThreadSerializer,
    OrganizationDetailSerilizer,
)

from threadio.choices import ThreadKind
from threadio.models import Inbox, Thread


class PrivateOrganizationThreadReplySerializer(serializers.ModelSerializer):
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
            "is_read",
        ]

        read_only_fields = [
            "is_send_by_customer",
            "is_read",
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
            is_send_by_customer=False,
            **validated_data,
        )

        inbox = Inbox.objects.filter(
            thread=parent,
            organization=request_user.get_organization(),
        ).first()
        if inbox:
            inbox.unread_count = 1
            inbox.save()

        return thread


class PrivateOrganizationThreadSerializer(serializers.ModelSerializer):
    author = UserSlimSerializer(read_only=True)
    customer_slug = serializers.SlugRelatedField(
        slug_field="uid", queryset=OrganizationUser.objects.filter(), write_only=True
    )
    last_message = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Thread
        fields = [
            "uid",
            "content",
            "author",
            "customer_slug",
            "last_message",
            "is_read",
            "is_send_by_customer",
        ]

        read_only_fields = [
            "is_send_by_customer",
            "is_read",
        ]

    def validate_customer_slug(self, customer_slug):
        # Access the request object from the serializer's context
        request = self.context.get("request")

        if request:
            user = customer_slug.user
            organization = user.get_organization()

            # Query the OrganizationUser to get the slug of the customer
            customer = OrganizationUser.objects.filter(
                user=user,
                organization=organization,
                role=OrganizationUserRole.CUSTOMER,
            ).first()

            if customer and customer.uid == customer_slug.uid:
                return customer_slug  # Return the valid customer_slug
            else:
                raise serializers.ValidationError(
                    "You can not send message other organization's customer"
                )
        else:
            raise serializers.ValidationError("Request context not found.")

    def get_last_message(self, object_):
        last_message = (
            Thread.objects.select_related("author")
            .filter(Q(parent=object_) | Q(pk=object_.pk))
            .order_by("-created_at")
            .first()
        )
        return LastThreadSerializer(last_message).data

    def create(self, validated_data):
        # target = validated_data.pop("target", None)
        request_user = self.context["request"].user
        organization = request_user.get_organization()
        customer = validated_data.pop("customer_slug").user

        threads = Thread.objects.filter(
            inbox__organization=request_user.get_organization(), kind=ThreadKind.PARENT
        )

        inbox = Inbox.objects.filter(
            thread__in=list(threads), organization=organization, user=customer
        ).first()

        if inbox:
            thread = Thread.objects.create(
                parent=inbox.thread,
                author=request_user,
                kind=ThreadKind.CHILD,
                is_send_by_customer=False,
                **validated_data,
            )
            inbox.unread_count += 1
            inbox.save()

        else:
            thread = Thread.objects.create(
                author=request_user,
                kind=ThreadKind.PARENT,
                is_send_by_customer=False,
                **validated_data,
            )
            Inbox.objects.create(
                thread=thread,
                user=customer,
                organization=organization,
            )

            Inbox.objects.filter(thread=thread, organization=organization).update(
                unread_count=1
            )

        return thread
