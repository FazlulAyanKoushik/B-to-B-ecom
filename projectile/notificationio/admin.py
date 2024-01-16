from django.contrib import admin

from notificationio.models import (
    NotificationUserPreference,
    Notification,
    NotificationModelConnector,
    NotificationUserReceiver,
)


@admin.register(NotificationUserPreference)
class NotificationUserPreferenceAdmin(admin.ModelAdmin):
    model = NotificationUserPreference
    list_display = ["uid", "user"]
    readonly_fields = ["uid", "created_at", "updated_at"]


class NotificationModelConnectorInlineAdmin(admin.StackedInline):
    model = NotificationModelConnector


class NotificationUserReceiverInlineAdmin(admin.TabularInline):
    model = NotificationUserReceiver


@admin.register(NotificationUserReceiver)
class NotificationUserReceiverAdmin(admin.ModelAdmin):
    model = NotificationUserReceiver
    list_display = ["uid", "notification", "user", "is_read"]
    readonly_fields = ["uid", "created_at", "updated_at"]
    list_filter = ["is_read"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    model = Notification
    list_display = ["uid", "organization", "is_success", "action_type"]
    readonly_fields = ["uid", "created_at", "updated_at"]
    inlines = [
        NotificationModelConnectorInlineAdmin,
        NotificationUserReceiverInlineAdmin,
    ]

    def has_add_permission(self, request):
        return False

    # def has_change_permission(self, request, obj=None):
    #     return False
