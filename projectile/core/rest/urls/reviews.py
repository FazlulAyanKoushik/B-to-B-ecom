from django.urls import path

from ..views import reviews

urlpatterns = [
    path(
        "/<uuid:uid>",
        reviews.GlobalReviewDetailView.as_view(),
        name="private-review-details",
    ),
    path("", reviews.GlobalReviewListView.as_view(), name="private-review-list"),
]
