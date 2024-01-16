import logging

from django.db.models import Q, Max

from rest_framework.generics import ListCreateAPIView, get_object_or_404

from ..permissions import IsOrganizationStaff

from threadio.choices import ThreadKind
from threadio.models import Thread, Inbox

from ..serializers.inbox import (
    PrivateOrganizationThreadReplySerializer,
    PrivateOrganizationThreadSerializer,
)

logger = logging.getLogger(__name__)


class PrivateOrganizationThreadList(ListCreateAPIView):
    serializer_class = PrivateOrganizationThreadSerializer
    permission_classes = [IsOrganizationStaff]

    def get_queryset(self):
        return (
            Thread.objects.select_related("author")
            .filter(
                inbox__organization=self.request.user.get_organization(),
                kind=ThreadKind.PARENT,
            )
            .annotate(last_message_time=Max("replies__created_at"))
            .order_by("-last_message_time", "-created_at")
        )


class PrivateOrganizationThreadReplyList(ListCreateAPIView):
    serializer_class = PrivateOrganizationThreadReplySerializer
    permission_classes = [IsOrganizationStaff]

    def get_queryset(self):
        uid = self.kwargs.get("uid", None)
        parent = get_object_or_404(
            Thread.objects.select_related("author").filter(),
            uid=uid,
        )
        try:
            inbox = Inbox.objects.filter(
                thread=parent, organization=self.request.user.get_organization()
            ).first()
            if inbox and inbox.unread_count > 0:
                inbox.mark_as_read()

        except Inbox.DoesNotExist:
            logger.debug("Inbox object does not exist.")

        threads = (
            Thread.objects.select_related("author")
            .filter(Q(parent=parent) | Q(pk=parent.pk))
            .order_by("-created_at")
        )
        last_thread = threads.last()
        last_thread.is_read = True
        last_thread.save()

        return threads.exclude(content="")
