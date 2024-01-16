from django.apps import AppConfig


class AccountioConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accountio"

    def ready(self):
        from . import signals
