from django.db import models


class AddressStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    ACTIVE = "ACTIVE", "Active"
    REMOVED = "REMOVED", "Removed"
