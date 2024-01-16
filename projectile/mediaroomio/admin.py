from django.contrib import admin

from mediaroomio.models import MediaImage


# Register your models here.
@admin.register(MediaImage)
class MediaImageAdmin(admin.ModelAdmin):
    model = MediaImage
    list_display = [
        "uid",
        "caption",
    ]
