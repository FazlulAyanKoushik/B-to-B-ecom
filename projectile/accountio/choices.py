from django.db import models


class OrganizationStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    PLACEHOLDER = "PLACEHOLDER", "Placeholder"
    PENDING = "PENDING", "Pending"
    ACTIVE = "ACTIVE", "Active"
    HIDDEN = "HIDDEN", "Hidden"
    REMOVED = "REMOVED", "Removed"


class OrganizationUserRole(models.TextChoices):
    OWNER = "OWNER", "Owner"
    ADMIN = "ADMIN", "Admin"
    MANAGER = "MANAGER", "Manager"
    STAFF = "STAFF", "Staff"
    CUSTOMER = "CUSTOMER", "Customer"
    DELIVERER = "DELIVERER", "Deliverer"


class OrganizationUserStatus(models.TextChoices):
    INVITED = "INVITED", "Invited"
    PENDING = "PENDING", "Pending"
    ACTIVE = "ACTIVE", "Active"
    SUSPEND = "SUSPEND", "Suspend"
    REJECTED = "REJECTED", "Rejected"
    DEACTIVATE = "DEACTIVATE", "Deactivate"
    HIDDEN = "HIDDEN", "Hidden"
    REMOVED = "REMOVED", "Removed"
