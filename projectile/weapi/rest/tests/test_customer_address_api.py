from rest_framework import status

from accountio.choices import OrganizationUserRole
from common.base_orm import BaseOrmCallApi
from common.base_test import BaseAPITestCase

from core.rest.tests import urlhelpers as core_urlhelpers

from weapi.rest.tests import payloads, urlhelpers


class PrivateCustomerAddressApiTests(BaseAPITestCase):
    """Test customer address api"""

    def setUp(self):
        super(PrivateCustomerAddressApiTests, self).setUp()

        self.base_orm = BaseOrmCallApi()

        # Create customer
        self.create_customer = self.client.post(
            core_urlhelpers.user_registration_list_url(),
            payloads.create_customer_payload(),
        )
        # login
        self.customer_login = self.client.post(
            core_urlhelpers.user_token_login_url(), payloads.customer_login_payload()
        )
        self.user = self.base_orm.get_user("+8801311449836")

        # creating organization with user me_detail_url
        organization = self.base_orm.create_organization("mirpur pharma")
        self.base_orm.create_organization_user(
            organization=organization,
            user=self.user,
            role=OrganizationUserRole.CUSTOMER,
        )

        # Assert that the response is correct
        self.assertEqual(self.create_customer.status_code, status.HTTP_201_CREATED)

        # Login customer
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + self.customer_login.data["access"],
            X_DOMAIN=organization.domain,
        )
        # Assert that the response is correct
        self.assertEqual(self.customer_login.status_code, status.HTTP_201_CREATED)

        # Create upazila, district, and division for customer address
        self.division = self.base_orm.division("Dhaka")
        self.district = self.base_orm.district("Gazipur", self.division.name)
        self.upazila = self.base_orm.upazila("Dhamrai", self.district.name)

        # Create customer address
        self.customer_address = self.client.post(
            urlhelpers.customer_address_list_url(),
            payloads.customer_address_payload(
                self.upazila.uid, self.district.uid, self.division.uid
            ),
        )
        # Get customer address
        self.get_customer_address = self.client.get(
            urlhelpers.customer_address_list_url()
        )

        # Get customer address uid
        self.customer_address_uid = self.get_customer_address.data[0]["uid"]

    def test_create_customer_address(self):
        # Test create customer address api

        response = self.customer_address

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["house_street"],
            payloads.customer_address_payload(
                self.upazila.uid, self.district.uid, self.division.uid
            )["house_street"],
        )

    def test_get_customer_address_list(self):
        # Test get customer address list api

        response = self.get_customer_address

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data[0]["label"],
            payloads.customer_address_payload(
                self.upazila.uid, self.district.uid, self.division.uid
            )["label"],
        )

    def test_get_customer_address_detail(self):
        # Test get customer address detail api

        response = self.client.get(
            urlhelpers.customer_address_detail_url(self.customer_address_uid)
        )
        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["country"],
            payloads.customer_address_payload(
                self.upazila.uid, self.district.uid, self.division.uid
            )["country"],
        )

    def test_update_customer_address_detail(self):
        # Test updated customer address detail api

        payload = {"label": "Khan ABC Tradeplex"}

        response = self.client.patch(
            urlhelpers.customer_address_detail_url(self.customer_address_uid), payload
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["label"], payload["label"])

    def test_delete_customer_address(self):
        # Test customer address delete api

        response = self.client.delete(
            urlhelpers.customer_address_detail_url(self.customer_address_uid)
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
