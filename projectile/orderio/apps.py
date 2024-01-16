from django.apps import AppConfig


class OrderioConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orderio"

    def ready(self):
        from . import signals
