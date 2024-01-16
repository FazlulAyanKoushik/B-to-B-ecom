from rest_framework import status

from common.base_orm import BaseOrmCallApi
from common.base_test import BaseAPITestCase

from . import payloads, urlhelpers


class PrivateProductSearchApiTest(BaseAPITestCase):
    """Test product search api"""

    def setUp(self):
        super(PrivateProductSearchApiTest, self).setUp()

        self.base_orm = BaseOrmCallApi()

        # Create base product
        self.base_product = self.base_orm.baseproduct(payloads.base_product_payload())

        # Get base product uid
        self.base_product_uid = self.base_product.uid

        # Get organization
        self.organization = self.client.get(urlhelpers.organization_list_url())

        # Get organization user uid
        self.user = self.client.get(urlhelpers.organization_user_list_url())
        self.user_uid = self.user.data["results"][0]["user"]["uid"]

        # Create product payload
        self.payload = {
            "base_product": self.base_product_uid,
            "organization": self.organization,
            "stock": 10,
            "selling_price": "100",
            "merchant": self.user_uid,
        }

        # Create product
        self.post_response = self.client.post(
            urlhelpers.product_list_url(), self.payload
        )

        # Assert that the response is correct
        self.assertEqual(self.post_response.status_code, status.HTTP_201_CREATED)

    def test_search_base_product(self):
        # Test search product api

        response = self.client.get(
            urlhelpers.search_base_product_url(), {"name": "Napa"}
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["name"], "Napa")
        self.assertEqual(response.data["count"], 1)

    def test_search_product(self):
        # Test search private product api

        response = self.client.get(urlhelpers.search_product_url(), {"name": "Napa"})

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["name"], "Napa")
        self.assertEqual(response.data["count"], 1)
