from typing import Optional, List

from redis_om import EmbeddedJsonModel, JsonModel, Field

from redisio.pydantic.images import ImagePy, ImageThroughPy
from redisio.services import redis_connection


class TagsPy(EmbeddedJsonModel):
    uid: str = Field(index=False)
    category: Optional[str] = Field(index=False)
    name: str = Field(index=False)
    i18n: Optional[str] = Field(index=False)
    slug: str = Field(index=False)
    status: Optional[str] = Field(index=False)


class ProductPy(JsonModel):
    slug: str = Field(index=False)
    uid: str = Field(index=False)
    name: str = Field(index=True, full_text_search=True)
    stock: int = Field(index=False)
    unit: str = Field(index=False)
    strength: str = Field(index=False)
    buying_price: str = Field(index=False)
    selling_price: str = Field(index=False)
    fraction_mrp: int = Field(index=False)
    discount_price: str = Field(index=False)
    final_price: str = Field(index=False)
    status: str = Field(index=False)
    manufacturer: str = Field(index=False)
    brand: str = Field(index=False)
    dosage_form: str = Field(index=False)
    description: str = Field(index=False)
    category: str = Field(index=False)
    active_ingredients: List[str] = Field(index=False)
    primary_image = ImagePy
    total_images: List[ImageThroughPy] = ImageThroughPy
    tags: List[TagsPy] = TagsPy
    damage_stock: int = Field(index=False)
    box_type: str = Field(index=False)

    class Meta:
        database = redis_connection
