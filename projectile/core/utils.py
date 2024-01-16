import io
import os
import random
import string
import uuid

from PIL import Image
from dirtyfields import DirtyFieldsMixin
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken


class BaseModelwithUID(DirtyFieldsMixin, models.Model):
    class Meta:
        abstract = True

    uid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def generate_image() -> InMemoryUploadedFile:
    img = Image.new("RGB", (100, 100), color=(73, 109, 137))
    img_io = io.BytesIO()
    img.save(img_io, "JPEG")
    img_file = InMemoryUploadedFile(
        img_io,
        None,
        "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(15)
        )
        + ".jpg",
        "image/jpeg",
        img_io.getbuffer().nbytes,
        None,
    )
    return img_file


def generate_medicine_image() -> InMemoryUploadedFile:
    # Get the path to the static folder
    static_folder = os.path.join(settings.BASE_DIR, "static/images")

    # Get a list of all the image files in the static folder
    image_files = [
        f
        for f in os.listdir(static_folder)
        if f.endswith(".jpg") or f.endswith(".png") or f.endswith(".gif")
    ]

    # Choose a random image file
    image_file = random.choice(image_files)

    img1 = Image.open(os.path.join(static_folder, image_file))
    img_io1 = io.BytesIO()
    img1.save(img_io1, "JPEG")
    img_file = InMemoryUploadedFile(
        img_io1,
        None,
        "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(15)
        )
        + ".jpg",
        "image/jpeg",
        img_io1.getbuffer().nbytes,
        None,
    )
    return img_file


def create_token(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh), str(
        refresh.access_token
    )  # first return refresh_token and second one is access_token


def get_slug_full_name(instance):
    name = f"{instance.first_name} {instance.last_name}"
    return name.strip()
