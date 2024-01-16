from django.db import models

from .choices import OrganizationStatus, OrganizationUserStatus


class OrganizationQuerySet(models.QuerySet):
    def get_status_active(self):
        return self.filter(status=OrganizationStatus.ACTIVE)

    def get_status_editable(self):
        statuses = [
            OrganizationStatus.ACTIVE,
            OrganizationStatus.DRAFT,
            OrganizationStatus.HIDDEN,
            OrganizationStatus.PENDING,
        ]
        return self.filter(status__in=statuses)


class OrganizationUserQuerySet(models.QuerySet):
    def get_status_active(self):
        return self.filter(status=OrganizationUserStatus.ACTIVE)

    def get_status_editable(self):
        statuses = [
            OrganizationUserStatus.INVITED,
            OrganizationUserStatus.PENDING,
            OrganizationUserStatus.ACTIVE,
            OrganizationUserStatus.HIDDEN,
        ]
        return self.filter(status__in=statuses)
