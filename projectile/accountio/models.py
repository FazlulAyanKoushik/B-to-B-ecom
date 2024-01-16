from autoslug import AutoSlugField

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q, UniqueConstraint

from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords

from versatileimagefield.fields import PPOIField, VersatileImageField

from common.utils import unique_number_generator

from core.utils import BaseModelwithUID

from .choices import OrganizationStatus, OrganizationUserRole, OrganizationUserStatus
from .managers import OrganizationQuerySet, OrganizationUserQuerySet

User = get_user_model()


class Organization(BaseModelwithUID):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(
        populate_from="name",
        unique=True,
        verbose_name="This is domain",
        unique_with="name",
    )
    domain = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="By default, it will use SLUG as domain. But if you have a domain, you can write down your domain here instance using SLUG.",
    )
    kind = models.CharField(max_length=40, db_index=True, blank=True)
    tax_number = models.CharField(max_length=255, blank=True)
    registration_no = models.CharField(max_length=50, blank=True)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Links to other external urls
    contact_number = PhoneNumberField(blank=True)
    website_url = models.URLField(blank=True)
    blog_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    whatsapp_number = PhoneNumberField(blank=True)
    imo_number = models.CharField(blank=True, max_length=12)
    summary = models.CharField(
        max_length=1000, blank=True, help_text="Short summary about company."
    )
    description = models.CharField(
        max_length=1000, blank=True, help_text="Longer description about company."
    )
    store_front_photo = VersatileImageField(
        width_field="width",
        height_field="height",
        ppoi_field="ppoi",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=OrganizationStatus.choices,
        db_index=True,
        default=OrganizationStatus.DRAFT,
    )
    width = models.PositiveIntegerField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    ppoi = PPOIField()

    logo = VersatileImageField(
        width_field="logo_width",
        height_field="logo_height",
        ppoi_field="logo_ppoi",
        null=True,
        blank=True,
    )
    logo_width = models.PositiveIntegerField(blank=True, null=True)
    logo_height = models.PositiveIntegerField(blank=True, null=True)
    logo_ppoi = PPOIField()

    # custom managers use
    objects = OrganizationQuerySet.as_manager()

    # history
    history = HistoricalRecords()

    def __str__(self):
        return f"Name: {self.name}, Slug: {self.slug}, Kind: {self.kind}"

    def get_users(self):
        statuses = [OrganizationUserStatus.PENDING, OrganizationUserStatus.ACTIVE]
        roles = [
            OrganizationUserRole.STAFF,
            OrganizationUserRole.ADMIN,
            OrganizationUserRole.OWNER,
        ]
        return self.organizationuser_set.filter(role__in=roles, status__in=statuses)

    def get_customers(self):
        statuses = [OrganizationUserStatus.PENDING, OrganizationUserStatus.ACTIVE]
        roles = [
            OrganizationUserRole.CUSTOMER,
        ]
        return self.organizationuser_set.filter(role__in=roles, status__in=statuses)

    def add_owner(self, user):
        return OrganizationUser.objects.create(
            organization=self,
            user=user,
            role=OrganizationUserRole.OWNER,
            status=OrganizationUserStatus.ACTIVE,
            is_default=True,
        )

    def add_admin(self, user):
        return OrganizationUser.objects.create(
            organization=self,
            user=user,
            role=OrganizationUserRole.ADMIN,
            status=OrganizationUserStatus.ACTIVE,
            is_default=True,
        )

    def add_staff(self, user):
        return OrganizationUser.objects.create(
            organization=self,
            user=user,
            role=OrganizationUserRole.STAFF,
            status=OrganizationUserStatus.ACTIVE,
            is_default=True,
        )

    def is_status_draft(self):
        return self.status == OrganizationStatus.DRAFT

    def is_status_placeholder(self):
        return self.status == OrganizationStatus.PLACEHOLDER

    def is_status_pending(self):
        return self.status == OrganizationStatus.PENDING

    def is_status_active(self):
        return self.status == OrganizationStatus.ACTIVE

    def set_status_pending(self):
        self.status = OrganizationStatus.PENDING
        self.save_dirty_fields()

    def set_status_active(self):
        self.status = OrganizationStatus.ACTIVE
        self.save_dirty_fields()

    def set_status_removed(self):
        # Soft delete because there might be linked data
        self.status = OrganizationStatus.REMOVED
        self.save(update_fields=["status", "updated_at"])
        self.organizationuser_set.filter().update(status=OrganizationUserStatus.REMOVED)


class OrganizationUser(BaseModelwithUID):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    discount_offset = models.SmallIntegerField(
        default=0,
        help_text="We accept only percent here. For product, we will update the final price of a product regarding this percent.",
    )
    role = models.CharField(
        choices=OrganizationUserRole.choices,
        max_length=20,
    )
    status = models.CharField(
        max_length=20,
        choices=OrganizationUserStatus.choices,
        default=OrganizationUserStatus.PENDING,
    )
    is_default = models.BooleanField(default=False)

    # custom managers use
    objects = OrganizationUserQuerySet.as_manager()

    # history
    history = HistoricalRecords()

    class Meta:
        unique_together = (
            "organization",
            "user",
        )
        constraints = [
            UniqueConstraint(
                fields=["user"],
                condition=Q(is_default=True),
                name="user_have_one_default_organization",
                violation_error_message="A merchant can have only one default organization.",
            )
        ]

    def __str__(self):
        return f"ID: {self.id}, Org: {self.organization}, User: {self.user}, Role: {self.role}, Status: {self.status}"

    def set_role_staff(self):
        self.role = OrganizationUserRole.STAFF
        self.save_dirty_fields()

    def set_role_owner(self):
        self.role = OrganizationUserRole.OWNER
        self.save_dirty_fields()

    def set_status_pending(self):
        self.status = OrganizationUserStatus.PENDING
        self.save_dirty_fields()

    def set_status_active(self):
        self.status = OrganizationUserStatus.ACTIVE
        self.save_dirty_fields()

    def set_status_hidden(self):
        self.status = OrganizationUserStatus.HIDDEN
        self.save_dirty_fields()

    def set_status_suspend(self):
        self.status = OrganizationUserStatus.SUSPEND
        self.save_dirty_fields()

    def set_status_deactivate(self):
        self.status = OrganizationUserStatus.DEACTIVATE
        self.save_dirty_fields()

    def set_status_removed(self):
        self.status = OrganizationUserStatus.REMOVED
        self.save_dirty_fields()

    def set_discount_offset(self, discount_offset=0):
        self.discount_offset = discount_offset
        self.save_dirty_fields()

    def select(self):
        self.is_default = True
        self.save_dirty_fields()

    def accept(self):
        self.status = OrganizationUserStatus.ACTIVE
        fields = ["status"]
        if not self.user.users.filter(user=self.user, is_default=True).exists():
            fields.append("is_default")
            self.is_default = True
        self.save()

    def reject(self):
        self.status = OrganizationUserStatus.REJECTED
        self.save_dirty_fields()


class TransactionOrganizationUser(BaseModelwithUID):
    serial_number = models.PositiveIntegerField(unique=True, blank=True, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(
        "orderio.Order", on_delete=models.CASCADE, null=True, blank=True
    )
    total_money = models.DecimalField(max_digits=10, decimal_places=2)
    payable_money = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=700, blank=True)

    # history
    history = HistoricalRecords()

    def __str__(self):
        return f"User: {self.user.get_name()}, payable_money: {self.payable_money}"

    class Meta:
        unique_together = ("order", "organization")

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.serial_number = unique_number_generator(self)
        super().save(*args, **kwargs)
