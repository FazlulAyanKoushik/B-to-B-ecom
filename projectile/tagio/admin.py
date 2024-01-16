from django.contrib import admin

from .models import Tag, TagConnector


class TagConnectorInline(admin.TabularInline):
    model = TagConnector


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["uid", "parent", "category", "name", "slug", "status", "updated_at"]
    list_filter = ["status", "created_at", "updated_at"]
    search_fields = ["name", "slug"]
    inlines = (TagConnectorInline,)


@admin.register(TagConnector)
class TagAdmin(admin.ModelAdmin):
    list_display = ["uid", "organization"]
