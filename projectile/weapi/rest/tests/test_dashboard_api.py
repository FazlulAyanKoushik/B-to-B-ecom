from rest_framework import status

from common.base_orm import BaseOrmCallApi
from common.base_test import BaseAPITestCase

from . import payloads, urlhelpers


class PrivateDashboardApiTest(BaseAPITestCase):
    """Test dashboard list api"""

    def setUp(self):
        super(PrivateDashboardApiTest, self).setUp()

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

    def test_get_dashboard_list(self):
        # Test get dashboard list api

        response = self.client.get(urlhelpers.dashboard_list_url())

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["product_stock_price_sum"], "1000.00")
        self.assertEqual(
            response.data["categories_product"][0]["total_stock"], self.payload["stock"]
        )
