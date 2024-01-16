from django.db import models


class MediaImageKind(models.TextChoices):
    IMAGE = "IMAGE", "Image"
    VIDEO = "VIDEO", "Video"


class MediaImageConnectorKind(models.TextChoices):
    UNDEFINED = "UNDEFINED", "Undefined"
    BASE_PRODUCT = "BASE_PRODUCT", "Base Product"
    PRODUCT = "PRODUCT", "Product"
