from django.urls import path

from ..views.tags import PrivateTagDetail, PrivateTagList

urlpatterns = [
    path("/<uuid:uid>", PrivateTagDetail.as_view(), name="tag-detail"),
    path("", PrivateTagList.as_view(), name="tag-list"),
]
