from core.utils import BaseModelwithUID
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from .choices import AddressStatus

from .managers import AddressQuerySet

User = get_user_model()


class Division(BaseModelwithUID):
    name = models.CharField(max_length=255)
    bengali_name = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(
        max_digits=20, decimal_places=15, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=20, decimal_places=15, null=True, blank=True
    )

    def __str__(self):
        return self.name


class District(BaseModelwithUID):
    name = models.CharField(max_length=255)
    bengali_name = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(
        max_digits=20, decimal_places=15, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=20, decimal_places=15, null=True, blank=True
    )
    division = models.ForeignKey(
        Division, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.name


class Upazila(BaseModelwithUID):
    """
    this is also police station
    """

    name = models.CharField(max_length=255)
    bengali_name = models.CharField(max_length=255, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ("name", "district", "division")


class Address(BaseModelwithUID):
    label = models.CharField(max_length=255, blank=True)
    house_street = models.CharField(
        verbose_name="House and street", max_length=255, blank=True
    )
    upazila = models.ForeignKey(
        Upazila, on_delete=models.SET_NULL, null=True, blank=True
    )
    division = models.ForeignKey(
        Division, on_delete=models.SET_NULL, null=True, blank=True
    )
    district = models.ForeignKey(
        District, on_delete=models.SET_NULL, null=True, blank=True
    )
    country = models.CharField(
        verbose_name="Country name", max_length=255, blank=True, default="Bangladesh"
    )
    status = models.CharField(
        max_length=20,
        choices=AddressStatus.choices,
        db_index=True,
        default=AddressStatus.ACTIVE,
    )
    is_storefront = models.BooleanField(
        default=False, help_text="Checking if this address is a storefront or not."
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    organization = models.ForeignKey(
        "accountio.Organization", on_delete=models.SET_NULL, null=True, blank=True
    )
    objects = AddressQuerySet.as_manager()

    def __str__(self):
        return f"Country: {self.country}"

    def clean(self):
        if not self.user and not self.organization:
            raise ValidationError("Either 'user' or 'organization' must be set.")

    def is_status_draft(self):
        return self.status == AddressStatus.DRAFT

    def is_status_active(self):
        return self.status == AddressStatus.ACTIVE

    def set_status_active(self):
        self.status = AddressStatus.ACTIVE
        self.save_dirty_fields()

    def removed(self):
        self.status = AddressStatus.REMOVED
        self.save_dirty_fields()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
