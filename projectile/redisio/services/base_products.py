from collections import deque

from redis_om import Migrator

from rest_framework.exceptions import ValidationError

from catalogio.models import Product, BaseProduct

from redisio.pydantic.baseproducts import BaseProductPy
from redisio.services import redis_connection

from weapi.rest.serializers.search import PrivateBaseProductSearchSerializer


class BaseProductRedisServices:
    def __init__(self):
        self._redis_connection = redis_connection
        Migrator().run()

    def _save_to_redis(self, serialize_data):
        # img_link = "https://devapi.pharmik.co"
        # img_link = "https://testapi.pharmik.co"
        img_link = "http://127.0.0.1:8000"

        image = serialize_data.get("image", {})

        if image:
            if not image["original"].startswith("http"):
                image["original"] = f'{img_link}{image["original"]}'
                image["at512"] = f'{img_link}{image["at512"]}'
                image["at256"] = f'{img_link}{image["at256"]}'

        base_product = BaseProductPy(
            uid=serialize_data.get("uid", ""),
            name=serialize_data.get("name", ""),
            description=serialize_data.get("description", ""),
            active_ingredients=serialize_data.get("active_ingredients", []) or [],
            dosage_form=serialize_data.get("dosage_form", "") or "",
            unit=serialize_data.get("unit", "") or "",
            strength=serialize_data.get("strength", "") or "",
            manufacturer=serialize_data.get("manufacturer", "") or "",
            brand=serialize_data.get("brand", "") or "",
            route_of_administration=serialize_data.get("route_of_administration", "")
            or "",
            medicine_physical_state=serialize_data.get("medicine_physical_state", "")
            or "",
            image=image,
            mrp=serialize_data.get("mrp", ""),
        )
        base_product.save()

    def _convert_to_serializer(self, request, instance):
        return PrivateBaseProductSearchSerializer(
            instance, context={"request": request}
        ).data

    def _get_a_base_product(self, pk=None, uid=None) -> BaseProduct:
        try:
            product = (
                BaseProduct.objects.select_related(
                    "category",
                    "manufacturer",
                    "brand",
                    "route_of_administration",
                    "medicine_physical_state",
                )
                .prefetch_related("active_ingredients")
                .filter(merchant_product__isnull=True)
                .order_by("brand__name", "-strength")
            )
            if pk:
                product = product.get(pk=pk)
            elif uid:
                product = product.get(uid=uid)
            else:
                raise ValueError("You have to provide product ID or UID")
            return product

        except Product.DoesNotExist:
            raise ValidationError({"detail": "Product cannot find in redis."})

    def save(self, request=None, pk=None, uid=None):
        product = self._get_a_base_product(pk=pk, uid=uid)
        # serialize the data as dict
        serialize_data = self._convert_to_serializer(request=request, instance=product)

        # save the serialize_data to redis as json
        self._save_to_redis(serialize_data)

    def search_by_base_product_name(self, name: str):
        search_products = BaseProductPy.find(BaseProductPy.name % f"{name}*")

        response_data = deque(maxlen=search_products.count())
        for product in search_products.all():
            response_data.appendleft(product.dict(exclude={"pk"}))

        return list(response_data)
