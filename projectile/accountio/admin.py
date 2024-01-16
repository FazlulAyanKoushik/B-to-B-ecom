from django.contrib import admin

from accountio.models import Organization, OrganizationUser, TransactionOrganizationUser
from addressio.models import Address


# Register your models here.


class OrganizationAddressInlineAdmin(admin.TabularInline):
    model = Address
    fk_name = "organization"


class OrganizationUserInlineAdmin(admin.TabularInline):
    model = OrganizationUser
    fk_name = "organization"


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    model = Organization
    list_display = [
        "uid",
        "name",
    ]
    readonly_fields = ["uid", "slug", "created_at", "updated_at"]
    inlines = (
        OrganizationAddressInlineAdmin,
        OrganizationUserInlineAdmin,
    )


@admin.register(OrganizationUser)
class OrganizationUserAdmin(admin.ModelAdmin):
    model = OrganizationUser
    list_display = ["uid", "role", "user", "organization", "is_default"]
    list_filter = ("role",)
    readonly_fields = ["uid", "created_at", "updated_at"]


@admin.register(TransactionOrganizationUser)
class TransactionOrganizationUserAdmin(admin.ModelAdmin):
    model = TransactionOrganizationUser
    list_display = [
        "serial_number",
        "order",
        "organization",
        "user",
        "total_money",
        "payable_money",
    ]
    search_fields = ["serial_number", "order__serial_number"]
    readonly_fields = ["uid", "created_at", "updated_at"]
