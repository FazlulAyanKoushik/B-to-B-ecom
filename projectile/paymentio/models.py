from autoslug import AutoSlugField
from django.db import models

from core.utils import BaseModelwithUID


class PaymentMethod(BaseModelwithUID):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name", unique=True, editable=False)

    def __str__(self):
        return self.name
