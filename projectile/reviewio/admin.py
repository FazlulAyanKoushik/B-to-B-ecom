from django.contrib import admin

from .models import Review

# Register your models here.


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    model = Review
    list_display = [
        "uid",
        "organization",
        "product",
        "order",
    ]
    readonly_fields = [
        "uid",
        "created_at",
        "updated_at",
    ]
