from django.db import models


class OrganizationUserRole(models.TextChoices):
    STAFF = "STAFF", "Staff"
    ADMIN = "ADMIN", "Admin"
    OWNER = "OWNER", "Owner"


class UserStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    PLACEHOLDER = "PLACEHOLDER", "Placeholder"
    ACTIVE = "ACTIVE", "Active"
    HIDDEN = "HIDDEN", "Hidden"
    PAUSED = "PAUSED", "Paused"
    REMOVED = "REMOVED", "Removed"
