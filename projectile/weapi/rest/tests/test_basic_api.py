from rest_framework import status

from common.base_orm import BaseOrmCallApi
from common.base_test import BaseAPITestCase

from . import payloads, urlhelpers


class PrivateBasicApiTests(BaseAPITestCase):
    """Test private basic api"""

    def setUp(self):
        super(PrivateBasicApiTests, self).setUp()
        self.base_orm = BaseOrmCallApi()

    def test_get_brand(self):
        # Test get brand list api

        # Create brand
        self.base_orm.brand()

        response = self.client.get(urlhelpers.brand_list_url())

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_category(self):
        # Test get category list api

        # Create category
        self.base_orm.category()

        response = self.client.get(urlhelpers.category_list_url())

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_ingredient(self):
        # Test get ingredient list api

        # Create ingredient
        self.base_orm.ingredient()

        response = self.client.get(urlhelpers.ingredient_list_url())

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_medicine_physical_state(self):
        # Test get medicine physical state list api

        # Create medicine physical state
        self.base_orm.medicine_physical_state()

        response = self.client.get(urlhelpers.medicine_physical_state_list_url())

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_route_of_administration(self):
        # Test get route of administration list api

        # Create route of administration
        self.base_orm.route_of_administration()

        response = self.client.get(urlhelpers.route_of_administration_list_url())

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_manufacturer_list(self):
        # Test get manufacturer list

        # create manufacturer
        self.base_orm.manufacturer()

        response = self.client.get(urlhelpers.manufacturer_list_url())

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_dosage_form_list(self):
        # Test get baseproduct's dosage_form list

        # create manufacturer
        self.base_orm.baseproduct(payloads.base_product_payload())

        response = self.client.get(urlhelpers.dosage_form_list_url())

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
