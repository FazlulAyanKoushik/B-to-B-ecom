from django.db import models

from autoslug import AutoSlugField

from core.utils import BaseModelwithUID

from .choices import TagCategory, TagEntity, TagStatus

from .utils import get_tag_slug


class Tag(BaseModelwithUID):
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    category = models.CharField(
        max_length=40, choices=TagCategory.choices, default=TagCategory.PRODUCT
    )
    name = models.CharField(max_length=40, unique=True)
    i18n = models.CharField(max_length=100, blank=True)
    slug = AutoSlugField(populate_from=get_tag_slug, unique=True)
    status = models.CharField(
        max_length=10, choices=TagStatus.choices, default=TagStatus.ACTIVE
    )

    class Meta:
        ordering = (
            "category",
            "name",
        )

    def __str__(self):
        return f"Category: {TagCategory(self.category).label}, Name: {self.name}, slug: {self.slug}"


class TagConnector(BaseModelwithUID):
    organization = models.ForeignKey(
        "accountio.Organization", on_delete=models.CASCADE, null=True, blank=True
    )
    product = models.ForeignKey(
        "catalogio.Product", on_delete=models.CASCADE, null=True, blank=True
    )
    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, null=True, blank=True
    )
    entity = models.CharField(max_length=20, choices=TagEntity.choices, db_index=True)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Tag Connector"
        ordering = ("-created_at",)
        unique_together = (
            (
                "product",
                "tag",
            ),
        )
