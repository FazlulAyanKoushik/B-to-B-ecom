from django.db import models

from rest_framework.validators import ValidationError

from core.models import User
from core.utils import BaseModelwithUID

from accountio.models import Organization

from catalogio.models import Product

from orderio.models import Order


# Create your models here.
class Review(BaseModelwithUID):
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
    )
    feedback = models.TextField(
        blank=True,
        null=True,
    )
    given_by = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    # connector models
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    def save(self, *args, **kwargs):
        if not self.organization:
            if self.product:
                self.organization = self.product.organization
            elif self.order:
                self.organization = self.order.organization
            else:
                raise ValidationError({"detail": "Organization is empty"})

        super().save(*args, **kwargs)
