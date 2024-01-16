from django.urls import path

from ..views import images

urlpatterns = [
    path(
        "/<uuid:uid>",
        images.PrivateImageDetail.as_view(),
        name="image-detail",
    ),
]
