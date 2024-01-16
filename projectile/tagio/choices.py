from django.db import models


class TagCategory(models.TextChoices):
    PRODUCT = "PRODUCT", "Product"
    ORGANIZATION = "ORGANIZATION", "Organization"


class TagEntity(models.TextChoices):
    ORGANIZATION = "ORGANIZATION", "Organization"
    PRODUCT = "PRODUCT", "Product"
    USER = "USER", "User"


class TagStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    ACTIVE = "ACTIVE", "Active"
    HIDDEN = "HIDDEN", "Hidden"
    ARCHIVED = "ARCHIVED", "Archived"
    REMOVED = "REMOVED", "Removed"
