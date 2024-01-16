from rest_framework import status

from catalogio.rest.tests import urlhelpers as catalogio_urlhelpers

from common.base_orm import BaseOrmCallApi
from common.base_test import BaseAPITestCase

from core.rest.tests import urlhelpers as core_urlhelpers

from . import payloads, urlhelpers


class PrivateCartsApiTests(BaseAPITestCase):
    """Test carts api"""

    def setUp(self):
        super(PrivateCartsApiTests, self).setUp()

        self.base_orm = BaseOrmCallApi()

        # Create base product
        self.base_product = self.base_orm.baseproduct(payloads.base_product_payload())

        # Get organization
        self.organization = self.client.get(urlhelpers.organization_list_url())

        # Get organization user uid
        self.user = self.client.get(urlhelpers.organization_user_list_url())
        self.user_uid = self.user.data["results"][0]["user"]["uid"]

        # Create product payload
        self.payload = {
            "base_product": self.base_product.uid,
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

        # Get product list
        self.get_product = self.client.get(catalogio_urlhelpers.product_list_url())

        # Get product slug
        self.product_slug = self.get_product.data["results"][0]["slug"]

        # Create customer
        self.customer = self.client.post(
            core_urlhelpers.user_registration_list_url(),
            payloads.create_customer_payload(),
        )

        # Logged in customer
        self.customer_login = self.client.post(
            core_urlhelpers.user_token_login_url(), payloads.customer_login_payload()
        )

        # Provide customer credentials for access restricted api
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + self.customer_login.data["access"],
            HTTP_X_DOMAIN="bill-corp",
        )

        # Add product on cart
        self.product = self.client.post(
            urlhelpers.cart_products_list_url(),
            payloads.add_product_payload(self.product_slug),
        )

        # Get product from cart
        self.get_product = self.client.get(urlhelpers.cart_products_list_url())

        # Get product slug
        self.product_slug = self.get_product.data["products"][0]["slug"]

    def test_product_added_on_carts(self):
        # Test product added on carts api

        response = self.product

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_product_from_carts(self):
        # Test get product from carts api

        response = self.get_product

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["products"][0]["quantity"],
            payloads.add_product_payload(self.product_slug)["quantity"],
        )

    def test_remove_product_from_carts(self):
        # Test remove product from carts api

        response = self.client.delete(
            urlhelpers.cart_products_remove_url(self.product_slug)
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
