from django.urls import path, include


urlpatterns = [
    path("", include("catalogio.rest.urls.products")),
]
