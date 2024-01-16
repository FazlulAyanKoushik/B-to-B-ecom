from django.urls import reverse


def district_list_url():
    return reverse("districts-list")


def district_list_url_by_division(division_uid):
    return reverse("district-list-by-division", args=[division_uid])


def division_list_url():
    return reverse("division-list")


def upazila_list_url():
    return reverse("upazila-list")


def get_upazila_list_by_district_url(district_uid):
    return reverse("upazila-list-by-district", args=[district_uid])
