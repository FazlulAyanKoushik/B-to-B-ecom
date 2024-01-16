from autoslug import AutoSlugField

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from simple_history.models import HistoricalRecords

from versatileimagefield.fields import PPOIField, VersatileImageField

from accountio.models import Organization
from addressio.models import District

from catalogio.utils import (
    get_product_slug,
    discount_price_calculator,
    get_base_product_slug,
)

from core.utils import BaseModelwithUID

from .choices import CategoryStatus, ProductStatus, ProductBoxType
from .managers import ProductQuerySet

User = get_user_model()


class Category(BaseModelwithUID):
    name = models.CharField(max_length=100, verbose_name="Category name")
    slug = AutoSlugField(populate_from="name", editable=False, unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategories",
    )
    image = VersatileImageField(
        width_field="width",
        height_field="height",
        ppoi_field="ppoi",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=50,
        choices=CategoryStatus.choices,
        db_index=True,
        default=CategoryStatus.PENDING,
    )
    width = models.PositiveIntegerField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    ppoi = PPOIField()

    def __str__(self):
        return self.name

    def removed(self):
        self.status = CategoryStatus.REMOVED
        self.save_dirty_fields()


class Brand(BaseModelwithUID):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name", editable=False, unique=True)
    image = VersatileImageField(
        width_field="width",
        height_field="height",
        ppoi_field="ppoi",
        null=True,
        blank=True,
    )
    width = models.PositiveIntegerField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    ppoi = PPOIField()

    def __str__(self):
        return self.name


class Ingredient(BaseModelwithUID):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name", editable=False, unique=True)

    def __str__(self):
        return self.name


class Manufacturer(BaseModelwithUID):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name", editable=False, unique=True)

    def __str__(self):
        return self.name


class DosageForm(BaseModelwithUID):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name", editable=False, unique=True)

    def __str__(self):
        return self.name


class Supplier(BaseModelwithUID):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name", editable=False, unique=True)

    def __str__(self):
        return self.name


class MedicinePhysicalState(BaseModelwithUID):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name", editable=False, unique=True)

    def __str__(self):
        return self.name


class RouteOfAdministration(BaseModelwithUID):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name", editable=False, unique=True)

    def __str__(self):
        return self.name


class DeliveryCharge(BaseModelwithUID):
    charge = models.DecimalField(max_digits=10, decimal_places=2)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            "district",
            "organization",
        )

    def __str__(self):
        return f"{self.district.name}: {self.charge}"


# Product


class BaseProduct(BaseModelwithUID):
    """
    the product which is created by superadmin is the main base product where merchant can inherit
    but if superadmin is null means that product is created by merchant which is not shown to merchant for suggestion,
     that product only for that merchant.

     we use merchant_product for track down the merchant product we can easily get the merchant product from here without making complex queries.
     merchant_slug: when a owner/admin of merchant want to see whole data for that merchant table, he can use easily from here to make a simple query.

    """

    superadmin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to=Q(is_superuser=True) | Q(is_staff=True),
    )
    merchant_product = models.OneToOneField(
        "catalogio.Product", on_delete=models.CASCADE, null=True, blank=True
    )

    name = models.CharField(max_length=255, db_index=True)
    slug = AutoSlugField(
        populate_from=get_base_product_slug,
        editable=False,
        unique=True,
        blank=True,
        null=True,
    )
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, blank=True, null=True
    )
    active_ingredients = models.ManyToManyField(Ingredient, blank=True)
    dosage_form = models.ForeignKey(
        DosageForm, on_delete=models.SET_NULL, null=True, blank=True
    )
    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.SET_NULL, null=True, blank=True
    )
    unit = models.CharField(max_length=100, blank=True)
    strength = models.CharField(max_length=100, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    route_of_administration = models.ForeignKey(
        RouteOfAdministration, null=True, blank=True, on_delete=models.SET_NULL
    )
    medicine_physical_state = models.ForeignKey(
        MedicinePhysicalState, null=True, blank=True, on_delete=models.SET_NULL
    )
    image = VersatileImageField(
        width_field="width",
        height_field="height",
        ppoi_field="ppoi",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=ProductStatus.choices,
        db_index=True,
        default=ProductStatus.PUBLISHED,
    )
    width = models.PositiveIntegerField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ppoi = PPOIField()

    # history
    history = HistoricalRecords()

    def __str__(self):
        return self.name


class Product(BaseModelwithUID):
    def name(self):
        return self.base_product.name

    base_product = models.ForeignKey(
        BaseProduct, on_delete=models.CASCADE, related_name="get_products"
    )
    organization = models.ForeignKey("accountio.Organization", on_delete=models.CASCADE)
    slug = AutoSlugField(populate_from=get_product_slug, editable=False, unique=True)
    stock = models.PositiveIntegerField(default=0)
    damage_stock = models.PositiveIntegerField(default=0)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fraction_mrp = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        help_text="we only accept percentage value.",
    )
    discount_price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="we only accept percentage value.",
    )
    merchant = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )  # only merchant who create this product
    image = VersatileImageField(
        width_field="width",
        height_field="height",
        ppoi_field="ppoi",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=ProductStatus.choices,
        db_index=True,
        default=ProductStatus.PUBLISHED,
    )
    box_type = models.CharField(
        max_length=20,
        choices=ProductBoxType.choices,
        default=ProductBoxType.WITH_BOX,
    )
    width = models.PositiveIntegerField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    ppoi = PPOIField()

    # custom managers use
    objects = ProductQuerySet.as_manager()

    # history
    history = HistoricalRecords()

    def __str__(self):
        return self.base_product.name

    class Meta:
        unique_together = ("organization", "base_product", "box_type")

    def primary_image(self):
        try:
            return self.image if self.image else self.base_product.image
        except:
            return None

    def total_images(self):
        product_images = self.mediaimageconnector_set.select_related("image").all()
        base_product_images = self.base_product.mediaimageconnector_set.select_related(
            "image"
        ).all()
        return product_images | base_product_images

    def save(self, *args, **kwargs):
        self.final_price = discount_price_calculator(
            selling_price=self.selling_price, discount_price=self.discount_price
        )
        return super(Product, self).save(*args, **kwargs)
