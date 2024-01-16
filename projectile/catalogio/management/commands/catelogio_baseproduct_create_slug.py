from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import QuerySet

from tqdm import tqdm

from catalogio.models import BaseProduct


class Command(BaseCommand):
    help = "Base product saved to redis cache"

    def handle(self, *args, **options):
        base_products: QuerySet[BaseProduct] = BaseProduct.objects.select_related(
            "brand"
        ).filter(merchant_product__isnull=True)

        for base_product in tqdm(base_products):
            with transaction.atomic():
                """
                convert name space into -
                example Napa extra 500 -> apa-extra-500
                """
                try:
                    base_product.name = (
                        base_product.brand.name.title() + " " + base_product.strength
                    ).strip()
                except:
                    base_product.name = base_product.name.title()

                base_product.save()
