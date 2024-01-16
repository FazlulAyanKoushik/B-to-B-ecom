from django.urls import path

from ..views import addresses

urlpatterns = [
    path("/districts", addresses.GlobalDistrictList.as_view(), name="districts-list"),
    path("/divisions", addresses.GlobalDivisionList.as_view(), name="division-list"),
    path("/upazilas", addresses.GlobalUpazilaList.as_view(), name="upazila-list"),
    path(
        "/divisions/<uuid:division_uid>/districts",
        addresses.DistrictListByDivision.as_view(),
        name="district-list-by-division",
    ),
    path(
        "/districts/<uuid:district_uid>/upazilas",
        addresses.UpazilaListByDistrict.as_view(),
        name="upazila-list-by-district",
    ),
]
