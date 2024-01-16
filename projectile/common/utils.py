import io
import random
import string

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile, SimpleUploadedFile


def generate_fake_image() -> InMemoryUploadedFile:
    upfile = io.BytesIO()
    pilimg = Image.new("RGB", (100, 100))
    pilimg.save(fp=upfile, format="JPEG")
    image = SimpleUploadedFile(
        "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(15)
        )
        + ".jpg",
        upfile.getvalue(),
        content_type="image/jpg",
    )
    return image


def unique_number_generator(instance) -> int:
    model = instance.__class__
    unique_number = random.randint(111111, 9999999)
    if model.objects.filter(serial_number=unique_number).exists():
        unique_number_generator(instance)
    return unique_number
