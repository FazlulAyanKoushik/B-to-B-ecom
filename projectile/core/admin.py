from django.contrib import admin
from django.contrib.auth import get_user_model

from accountio.models import OrganizationUser
from addressio.models import Address
from core.forms import UserCreationForm
from paymentio.models import PaymentMethod

# Register your models here.
User = get_user_model()


class OrganizationUserInline(admin.TabularInline):
    model = OrganizationUser
    fk_name = "user"


class AddressInline(admin.TabularInline):
    model = Address
    fk_name = "user"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ["uid", "first_name", "last_name", "phone"]
    fieldsets = (
        (None, {"fields": ("phone", "password", "new_password")}),
        (
            "Other",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "image",
                    "uid",
                    "slug",
                )
            },
        ),
        (
            "User Permission",
            {
                "fields": (
                    "is_superuser",
                    "is_staff",
                    "is_verified",
                    "is_active",
                )
            },
        ),
        ("Groups and Permissions", {"fields": ("groups", "user_permissions")}),
    )
    list_filter = ["is_superuser", "is_staff", "status"]
    search_fields = ("phone",)
    readonly_fields = ("password", "uid", "slug")
    form = UserCreationForm
    inlines = (OrganizationUserInline, AddressInline)
    ordering = ("-created_at",)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    model = PaymentMethod
    list_display = [
        "uid",
        "name",
    ]
    readonly_fields = ("slug",)
