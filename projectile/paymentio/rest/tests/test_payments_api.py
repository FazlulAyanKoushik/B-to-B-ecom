from rest_framework import status

from common.base_orm import BaseOrmCallApi
from common.base_test import BaseAPITestCase
from . import urlhelpers


class GlobalPaymentMethodApiTest(BaseAPITestCase):
    """Global payment method list api test"""

    def setUp(self):
        super(GlobalPaymentMethodApiTest, self).setUp()
        self.base_orm = BaseOrmCallApi()

    def test_get_payment_method(self):
        # Test paymenth method list api

        # Create a payment method for test
        payment_method = self.base_orm.payment_method()

        response = self.client.get(urlhelpers.payment_method_url())

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], payment_method.name)
