from typing import List

from redis_om import JsonModel, Field

from redisio.pydantic.images import ImagePy


class BaseProductPy(JsonModel):
    uid: str = Field(index=False)
    name: str = Field(index=True, full_text_search=True)
    description: str = Field(index=False)
    active_ingredients: List[str] = Field(index=False)
    dosage_form: str = Field(index=True, full_text_search=True)
    manufacturer: str = Field(index=False)
    unit: str = Field(index=True, full_text_search=True)
    strength: str = Field(index=False)
    brand: str = Field(index=False)
    route_of_administration: str = Field(index=False)
    medicine_physical_state: str = Field(index=False)
    image = ImagePy
    mrp: str
