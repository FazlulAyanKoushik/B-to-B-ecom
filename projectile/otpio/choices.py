from django.db import models


class UserPhoneOTPStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    CONSUMED = "CONSUMED", "Consumed"
