from django.apps import AppConfig


class NotificationioConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notificationio"

    def ready(self):
        ...
