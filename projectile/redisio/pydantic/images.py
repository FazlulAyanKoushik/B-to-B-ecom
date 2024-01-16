from redis_om import EmbeddedJsonModel, Field


class ImagePy(EmbeddedJsonModel):
    original: str = Field(index=False)
    at512: str = Field(index=False)
    at256: str = Field(index=False)


class ImageThroughPy(EmbeddedJsonModel):
    image = ImagePy
