from django.urls import path, include


urlpatterns = [
    path("/domains", include("accountio.rest.urls.subdomains")),
    path("/organizations", include("accountio.rest.urls.organizations")),
]
