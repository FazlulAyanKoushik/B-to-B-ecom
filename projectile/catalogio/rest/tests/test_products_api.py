from django.contrib.auth import get_user_model

from rest_framework import status

from accountio.models import OrganizationUser
from common.base_orm import BaseOrmCallApi
from common.base_test import BaseAPITestCase
from weapi.rest.tests import payloads as we_payloads, urlhelpers as we_urlhelpers
from . import urlhelpers

User = get_user_model()


class PrivateProductsApiTests(BaseAPITestCase):
    """Test products api"""

    def setUp(self):
        super(PrivateProductsApiTests, self).setUp()

        # Get organization
        self.organization = self.client.get(we_urlhelpers.organization_list_url())
        self.base_orm = BaseOrmCallApi()

        # Create base product
        self.base_product = self.base_orm.baseproduct(
            we_payloads.base_product_payload()
        )

        # Get base product uid
        self.base_product_uid = self.base_product.uid

        # Get user uid
        self.user = self.client.get(we_urlhelpers.organization_user_list_url())
        self.user_uid = self.user.data["results"][0]["user"]["uid"]

        # Add discount offset in the Organization User model
        user = User.objects.get(uid=self.user_uid)
        organization_user = OrganizationUser.objects.get(user=user)
        # Adding 10 percent of offset discount to the organization user
        organization_user.discount_offset = 10
        organization_user.save()

        # Create payload for product
        self.payload = {
            "base_product": self.base_product_uid,
            "organization": self.organization,
            "stock": 10,
            "selling_price": "100",
            "final_price": "100",
            "merchant": self.user_uid,
        }

        # Create product
        self.post_product = self.client.post(
            we_urlhelpers.product_list_url(), self.payload
        )

        # Assert that the response is correct
        self.assertEqual(self.post_product.status_code, status.HTTP_201_CREATED)

        # Get product list
        self.get_product = self.client.get(urlhelpers.product_list_url())

        # Get product slug
        self.get_product_slug = self.get_product.data["results"][0]["slug"]

    def test_get_product_list(self):
        # Test get product list api

        response = self.get_product

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["name"], self.base_product.name)
        # Assert that the final price is updated with discount offset
        self.assertEqual(response.data["results"][0]["final_price"], "90.00")

    def test_get_product_detail(self):
        # Test get product detail api

        response = self.client.get(urlhelpers.product_detail_url(self.get_product_slug))

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["stock"], self.payload["stock"])
        # Assert that the final price is updated with discount offset
        self.assertEqual(response.data["final_price"], "90.00")
