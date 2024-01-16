from rest_framework import status
from rest_framework.test import (
    APIClient,
    APITestCase,
)

from core.rest.tests import payloads as core_payloads, urlhelpers as core_urlhelpers

from weapi.rest.tests import payloads as we_payloads


class BaseAPITestCase(APITestCase):
    """Written BaseAPITestCase for not repeating the same code in the test"""

    def setUp(self):
        self.client = APIClient()

        # Create organization and organization user
        self.post_organization_and_user = self.client.post(
            core_urlhelpers.organization_register_list_url(),
            we_payloads.user_and_organization_payload(),
        )

        # Assert that the response is correct
        self.assertEqual(
            self.post_organization_and_user.status_code, status.HTTP_201_CREATED
        )

        # Logged in organization user
        self.user_login = self.client.post(
            core_urlhelpers.user_token_login_url(), core_payloads.login_info_payload()
        )

        # Assert that the response is correct
        self.assertEqual(self.user_login.status_code, status.HTTP_201_CREATED)

        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + self.user_login.data["access"],
            HTTP_X_DOMAIN="bill-corp",
        )

    # End of the test it will be run for logout
    def tearDown(self):
        self.client.logout()
