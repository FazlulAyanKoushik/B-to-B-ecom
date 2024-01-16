from django.db.models import TextChoices


class ThreadKind(TextChoices):
    PARENT = "PARENT", "Parent"
    CHILD = "CHILD", "Child"


class ThreadStatus(TextChoices):
    DRAFT = "DRAFT", "Draft"
    ACTIVE = "ACTIVE", "Active"
    ARCHIVE = "ARCHIVED", "Archived"
    REMOVE = "REMOVED", "Removed"


class InboxStatus(TextChoices):
    ACTIVE = "ACTIVE", "Active"
    ARCHIVE = "ARCHIVED", "Archived"
    REMOVE = "REMOVED", "Removed"
