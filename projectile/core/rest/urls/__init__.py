from django.urls import path, include

urlpatterns = [
    path("/me", include("core.rest.urls.me")),
]
