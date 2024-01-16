from django.db import models
from versatileimagefield.fields import PPOIField, VersatileImageField

from core.utils import BaseModelwithUID
from .choices import MediaImageConnectorKind, MediaImageKind
from .managers import MediaImageQuerySet


class MediaImage(BaseModelwithUID):
    image = VersatileImageField(
        width_field="width",
        height_field="height",
        ppoi_field="ppoi",
    )
    width = models.PositiveIntegerField(blank=True)
    height = models.PositiveIntegerField(blank=True)
    ppoi = PPOIField()
    caption = models.CharField(max_length=100, blank=True, null=True)
    copyright = models.CharField(max_length=100, blank=True, null=True)
    priority = models.BigIntegerField(default=0)
    kind = models.CharField(
        max_length=20, choices=MediaImageKind.choices, db_index=True
    )

    objects = MediaImageQuerySet.as_manager()

    class Meta:
        ordering = ("-created_at",)


class MediaImageConnector(BaseModelwithUID):
    image = models.OneToOneField(MediaImage, on_delete=models.CASCADE)
    base_product = models.ForeignKey(
        "catalogio.BaseProduct", on_delete=models.CASCADE, null=True, blank=True
    )
    product = models.ForeignKey(
        "catalogio.Product", on_delete=models.CASCADE, null=True, blank=True
    )
    kind = models.CharField(
        max_length=20,
        default=MediaImageConnectorKind.UNDEFINED,
        choices=MediaImageConnectorKind.choices,
        db_index=True,
    )
