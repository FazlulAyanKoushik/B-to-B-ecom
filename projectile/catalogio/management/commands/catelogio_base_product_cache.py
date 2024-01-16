from django.core.management import BaseCommand
from tqdm import tqdm

from catalogio.models import BaseProduct
from redisio.services.base_products import BaseProductRedisServices


class Command(BaseCommand):
    help = "Base product saved to redis cache"

    def handle(self, *args, **options):
        base_products = BaseProduct.objects.filter(
            merchant_product__isnull=True
        ).order_by("-id")
        redis_base_product = BaseProductRedisServices()

        for base_product in tqdm(base_products):
            redis_base_product.save(pk=base_product.id)
