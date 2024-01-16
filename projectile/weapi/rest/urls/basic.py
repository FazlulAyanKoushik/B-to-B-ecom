from django.urls import path

from ..views import basic

urlpatterns = [
    path("/brands", basic.PrivateBrandList.as_view(), name="brand-list"),
    path("/categories", basic.PrivateCategoryList.as_view(), name="category-list"),
    path(
        "/dosage-forms", basic.PrivateDosageFormList.as_view(), name="dosage-form-list"
    ),
    path("/ingredients", basic.PrivateIngredientList.as_view(), name="ingredient-list"),
    path(
        "/medicine-physical-states",
        basic.PrivateMedicinePhysicalStateList.as_view(),
        name="medicine-physical-state-list",
    ),
    path(
        "/manufacturers",
        basic.PrivateManufacturerList.as_view(),
        name="manufacturer-list",
    ),
    path(
        "/route-of-administrations",
        basic.PrivateRouteOfAdministrationList.as_view(),
        name="route-of-administration-list",
    ),
]
