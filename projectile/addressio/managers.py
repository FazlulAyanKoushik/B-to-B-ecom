from django.db import models

from .choices import AddressStatus


class AddressQuerySet(models.QuerySet):
    def get_status_active(self):
        return self.filter(status=AddressStatus.ACTIVE)

    def get_status_editable(self):
        statuses = [AddressStatus.ACTIVE, AddressStatus.DRAFT]
        return self.filter(status__in=statuses)
