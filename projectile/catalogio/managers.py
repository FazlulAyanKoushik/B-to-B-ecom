from django.db import models

from .choices import ProductStatus


class ProductQuerySet(models.QuerySet):
    def get_status_active(self):
        return self.filter(status=ProductStatus.PUBLISHED)

    def get_status_editable(self):
        statuses = [
            ProductStatus.PUBLISHED,
            ProductStatus.DRAFT,
            ProductStatus.HIDDEN,
            ProductStatus.ARCHIVED,
            ProductStatus.UNPUBLISHED,
        ]
        return self.filter(status__in=statuses)
