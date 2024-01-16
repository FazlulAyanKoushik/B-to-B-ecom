from django.contrib import admin
from django.utils.safestring import mark_safe

from mediaroomio.models import MediaImageConnector
from tagio.models import TagConnector
from .models import (
    Category,
    Brand,
    DosageForm,
    Supplier,
    Ingredient,
    Manufacturer,
    MedicinePhysicalState,
    RouteOfAdministration,
    DeliveryCharge,
    BaseProduct,
    Product,
)


# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = (
        "uid",
        "name",
        "parent",
        "updated_at",
    )

    list_filter = (
        "name",
        "parent",
    )


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    model = Brand
    list_display = (
        "uid",
        "name",
        "updated_at",
    )


@admin.register(DosageForm)
class DosageFormAdmin(admin.ModelAdmin):
    model = DosageForm
    list_display = (
        "uid",
        "name",
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    model = Ingredient
    list_display = (
        "uid",
        "name",
        "updated_at",
    )


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    model = Supplier
    list_display = (
        "uid",
        "name",
        "updated_at",
    )


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    model = Manufacturer
    list_display = (
        "uid",
        "name",
    )


@admin.register(MedicinePhysicalState)
class MedicinePhysicalStateAdmin(admin.ModelAdmin):
    model = MedicinePhysicalState
    list_display = (
        "uid",
        "name",
        "updated_at",
    )


@admin.register(RouteOfAdministration)
class RouteOfAdministrationAdmin(admin.ModelAdmin):
    model = RouteOfAdministration
    list_display = (
        "uid",
        "name",
        "updated_at",
    )


@admin.register(DeliveryCharge)
class DeliveryChargeAdmin(admin.ModelAdmin):
    model = DeliveryCharge
    list_display = ("uid", "charge", "district")


class BaseProductImageInline(admin.TabularInline):
    model = MediaImageConnector
    fk_name = "base_product"
    exclude = ("product",)


class ProductTagInline(admin.TabularInline):
    model = TagConnector


class ProductImageInline(admin.TabularInline):
    model = MediaImageConnector
    fk_name = "product"
    exclude = ("base_product",)
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj:
            return mark_safe(
                "".join(f'<img src="{obj.image.image.url}" style="max-height: 50px;">')
            )
        else:
            return "No images found."


@admin.register(BaseProduct)
class BaseProductAdmin(admin.ModelAdmin):
    model = BaseProduct
    list_display = ("uid", "name", "dosage_form")
    exclude = ("product",)
    readonly_fields = ("superadmin", "uid", "slug")
    inlines = (BaseProductImageInline,)
    search_fields = ("name",)
    list_filter = (("merchant_product", admin.EmptyFieldListFilter),)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.superadmin = request.user
        super().save_model(request, obj, form, change)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ("uid", "base_product", "stock", "slug", "organization")
    readonly_fields = ("slug", "total_images", "uid")
    list_filter = ("status",)
    inlines = (ProductImageInline, ProductTagInline)
    search_fields = ("base_product__name", "uid", "organization__domain")

    def total_images(self, obj):
        images = obj.total_images()
        if images:
            return mark_safe(
                "".join(
                    f'<img src="{img.image.image.url}" style="max-height: 100px;">'
                    for img in images
                )
            )
        else:
            return "No images found."
