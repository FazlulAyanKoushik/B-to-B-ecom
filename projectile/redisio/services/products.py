from django.db.models import Q, Case, When, Value, CharField

from rest_framework.exceptions import ValidationError

from catalogio.models import Product

from redisio.pydantic.products import ProductPy
from redisio.serializers.products import RedisProductsSerializer
from redisio.services import redis_connection


class ProductRedisServices:
    def __init__(self):
        self.redis_connection = redis_connection
        Migrator().run()

    def _save_to_redis(self, serialize_data):
        product = ProductPy(
            slug=serialize_data.get("slug", ""),
            uid=str(serialize_data.get("uid", "")),
            name=serialize_data.get("name", ""),
            stock=serialize_data.get("stock", 0),
            unit=serialize_data.get("unit", ""),
            strength=serialize_data.get("strength", ""),
            buying_price=str(serialize_data.get("buying_price", "")),
            selling_price=str(serialize_data.get("selling_price", "")),
            fraction_mrp=serialize_data.get("fraction_mrp", 0),
            discount_price=str(serialize_data.get("discount_price", "")),
            final_price=str(serialize_data.get("final_price", "")),
            status=serialize_data.get("status", ""),
            manufacturer=serialize_data.get("manufacturer", ""),
            brand=serialize_data.get("brand", ""),
            dosage_form=serialize_data.get("dosage_form", ""),
            description=serialize_data.get("description", ""),
            category=serialize_data.get("category", ""),
            active_ingredients=serialize_data.get("active_ingredients", []),
            primary_image=serialize_data.get("primary_image", {}),
            total_images=serialize_data.get("total_images", []),
            tags=serialize_data.get("tags", []),
            damage_stock=serialize_data.get("damage_stock", 0),
            box_type=serialize_data.get("box_type", ""),
        )
        product.save()

    def _convert_to_serializer(self, request, instance):
        return RedisProductsSerializer(instance, context={"request": request}).data

    def _get_a_product(self, pk=None, slug=None, uid=None) -> Product:
        try:
            return (
                Product.objects.prefetch_related(
                    "tagconnector_set", "mediaimageconnector_set"
                )
                .select_related("base_product")
                .annotate(
                    stock_status=Case(
                        When(stock__gte=10, then=Value("In_Stock")),
                        When(stock__gt=0, then=Value("Low")),
                        default=Value("Out_Of_Stock"),
                        output_field=CharField(),
                    )
                )
                .get(Q(pk=pk) | Q(slug=slug) | Q(uid=uid))
            )
        except Product.DoesNotExist:
            raise ValidationError({"detail": "Product cannot find in redis."})

    def save(self, request, pk=None, slug=None, uid=None):
        product = self._get_a_product(pk=pk, slug=slug, uid=uid)
        # serialize the data as dict
        serialize_data = self._convert_to_serializer(request=request, instance=product)

        # save the serialize_data to redis as json
        self._save_to_redis(serialize_data)

    def search_by_product_name(self, name: str):
        return ProductPy.find(ProductPy.name % f"{name}*").all()
