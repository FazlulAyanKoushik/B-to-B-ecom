import logging

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from common.base_orm import BaseOrmCallApi

from core.rest.tests import payloads as core_payloads
from core.rest.tests import urlhelpers as core_urlhelpers

from weapi.rest.tests import payloads as we_payloads

from .urlhelpers import (
    district_list_url,
    district_list_url_by_division,
    get_upazila_list_by_district_url,
    upazila_list_url,
    division_list_url,
)

logger = logging.getLogger(__name__)


class PublicDistritsTestCase(APITestCase):
    """Public Test Case for Districts"""

    def setUp(self):
        self.client = APIClient()
        self.base_orm = BaseOrmCallApi()
        # Create User Using Registration ListCreateApiView

    def test_districts_list(self):
        # Create district using orm calls
        district_one = self.base_orm.district("Dhaka", "Dhaka")
        district_two = self.base_orm.district("Gazipur", "dhaka")
        district_three = self.base_orm.district("Gopalganj", "Dhaka")
        logger.warning("Calling orm calls here for creating three district instance")

        # districts list for any user using ListApiView
        response = self.client.get(district_list_url())

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # assert that the returned data is correct
        self.assertEqual(response.data[0]["name"], district_one.name)

    def test_get_division_list(self):
        # Getting all division
        division_one = self.base_orm.division("Dhaka")
        division_two = self.base_orm.division("Khulna")
        division_three = self.base_orm.division("Borisal")
        logger.warning("Calling orm calls here for creating three division instance")

        # Division list for any user using ListApiView
        response = self.client.get(division_list_url())

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # assert that the returned data is correct
        self.assertEqual(len(response.data), 3)

    def test_get_upazila_list(self):
        # Getting all upazila
        upazila_one = self.base_orm.upazila("Feni Sadar", "Feni")
        upazila_two = self.base_orm.upazila("Porsuram", "Feni")
        upazila_three = self.base_orm.upazila("Fulgazi", "Feni")
        logger.warning("Calling orm calls here for creating three upazila instance")

        # Upazila list for any user using ListApiView
        response = self.client.get(upazila_list_url())

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # assert that the returned data is correct
        self.assertEqual(response.data[0]["name"], upazila_one.name)

    def test_district_list_by_division_uid(self):
        """Get all district lists by division"""

        division = self.base_orm.division("Dhaka")
        district_one = self.base_orm.district("Dhaka", division.name)
        district_two = self.base_orm.district("Gazipur", division.name)
        district_three = self.base_orm.district("Gopalganj", division.name)
        district_four = self.base_orm.district("Gopalganj", "Khulna")

        # creating url for district list including division_uid
        url = district_list_url_by_division(division.uid)

        # districts list of a division for any user using ListApiView
        response = self.client.get(url)

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # assert that the returned data is correct
        self.assertEqual(response.data[0]["name"], district_one.name)

    def test_get_upazila_list_by_district(self):
        """Get all the upazila according to the district"""
        district = self.base_orm.district("Feni", "Chattogram")
        upazila_one = self.base_orm.upazila("Feni-sadar", district.name)
        upazila_two = self.base_orm.upazila("Fulgazi", district.name)
        upazila_three = self.base_orm.upazila("Porsuram", district.name)
        upazila_four = self.base_orm.upazila("Sonagazi", "Noakhali")

        url = get_upazila_list_by_district_url(district.uid)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["name"], upazila_one.name)
