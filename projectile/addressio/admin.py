from django.contrib import admin

from addressio.models import Address, District, Upazila, Division


# Register your models here.
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    model = Address
    list_display = [
        "uid",
        "label",
        "district",
        "country",
    ]
    readonly_fields = ("uid",)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    model = District
    list_display = (
        "uid",
        "name",
    )


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    model = Division
    list_display = (
        "uid",
        "name",
    )


@admin.register(Upazila)
class UpazilaAdmin(admin.ModelAdmin):
    model = District
    list_display = (
        "uid",
        "name",
    )
