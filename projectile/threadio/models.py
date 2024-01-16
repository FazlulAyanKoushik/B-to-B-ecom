from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from core.utils import BaseModelwithUID

from .choices import InboxStatus, ThreadKind

User = get_user_model()


class Thread(BaseModelwithUID):
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )
    kind = models.CharField(
        max_length=20,
        choices=ThreadKind.choices,
        default=ThreadKind.PARENT,
    )
    content = models.TextField(blank=True)
    author = models.ForeignKey(
        User,
        related_name="author_set",
        help_text="The 'User' who created the feed.",
        on_delete=models.SET_NULL,
        null=True,
    )
    is_read = models.BooleanField(default=False)
    is_send_by_customer = models.BooleanField()

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"UID: {self.uid}"


class Inbox(BaseModelwithUID):
    thread = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=20,
        choices=InboxStatus.choices,
        default=InboxStatus.ACTIVE,
    )
    unread_count = models.BigIntegerField(default=0)
    seen_at = models.DateTimeField(auto_now_add=True)

    organization = models.ForeignKey(
        "accountio.Organization",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ("-updated_at",)
        index_together = ("user", "organization")
        unique_together = ("user", "organization")

    def __str__(self):
        return f"UID: {self.uid} Customer: {self.user}"

    def mark_as_read(self):
        self.unread_count = 0

        self.seen_at = timezone.now()
        self.save_dirty_fields()

