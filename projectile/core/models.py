from autoslug import AutoSlugField

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords

from versatileimagefield.fields import VersatileImageField, PPOIField

from .choices import UserStatus

from .managers import CustomUserManager

from .utils import BaseModelwithUID, get_slug_full_name


class User(AbstractBaseUser, PermissionsMixin, BaseModelwithUID):
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    slug = AutoSlugField(populate_from=get_slug_full_name, editable=False, unique=True)
    phone = PhoneNumberField(blank=True, unique=True, db_index=True)
    email = models.EmailField(blank=True)
    image = VersatileImageField(
        width_field="width",
        height_field="height",
        ppoi_field="ppoi",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=UserStatus.choices,
        db_index=True,
        default=UserStatus.ACTIVE,
    )
    is_active = models.BooleanField(default=True)
    width = models.PositiveIntegerField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    ppoi = PPOIField()

    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ("first_name", "last_name")
    # Managers
    objects = CustomUserManager()

    # history
    history = HistoricalRecords()

    def __str__(self):
        name = " ".join([self.first_name, self.last_name])
        return f"Phone: {str(self.phone)}, Name: {name}"

    def is_merchant(self):
        return self.organizationuser_set.filter().exists()

    def get_organization(self):
        return (
            self.organizationuser_set.filter().get(is_default=True).organization or None
        )

    def get_organization_list(self):
        return (
            self.organizationuser_set.filter()
            .filter(is_default=True)
            .values_list("organization", flat=True)
            or None
        )

    def get_my_organization_role(self):
        return self.organizationuser_set.get(is_default=True).role or None

    def get_merchent_organization_user(self):
        return self.organizationuser_set.get(is_default=True) or None

    # def get_organization_user(self):
    #     queryset = self.organizationuser_set.select_related(
    #         "organization", "user"
    #     ).filter(is_default=True)
    #     if queryset.exists():
    #         return queryset.order_by("-updated_at").first()
    #     return queryset.filter().order_by("-updated_at").first()

    # def get_organization_list(self):
    #     organization_user = self.get_organization_user()
    #     if organization_user:
    #         return self.get_organization_user().organization
    #     return None

    def get_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        name = f"{self.first_name} {self.last_name}"
        return name.strip()

    def activate(self):
        self.status = UserStatus.ACTIVE
        self.save_dirty_fields()
