from rest_framework import status
from rest_framework.test import (
    APIClient,
    APITestCase,
)

from . import urlhelpers, payloads


class GlobalRegistrationApiTest(APITestCase):
    """Test organization and customer registration api"""

    def setUp(self):
        self.client = APIClient()

        # Create organization
        self.create_organization = self.client.post(
            urlhelpers.organization_register_list_url(),
            payloads.organization_registration_payload(),
        )

        # Logged in organization user
        self.user_login = self.client.post(
            urlhelpers.user_token_login_url(),
            payloads.organization_user_login_payload(),
        )

        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + self.user_login.data["access"],
            HTTP_X_DOMAIN="zakir-corp",
        )

    def test_organization_registration(self):
        # Test global orgnaization registration api

        response = self.create_organization

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_customer_registration(self):
        # Test global customer registration api

        response = self.client.post(
            urlhelpers.user_registration_list_url(),
            payloads.user_registration_payload(),
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_organization_user_password_reset(self):
        # Test organization user password reset api

        passsword_reset_payload = {
            "password": "Pass1234",
            "new_password": "Pass12345",
            "confirm_password": "Pass12345",
        }

        response = self.client.put(
            urlhelpers.user_password_reset_url(),
            passsword_reset_payload,
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
