from rest_framework import status

from common.base_orm import BaseOrmCallApi
from common.base_test import BaseAPITestCase

from . import payloads, urlhelpers


class PrivateOrganizationApiTests(BaseAPITestCase):
    """Test organization api"""

    def setUp(self):
        super(PrivateOrganizationApiTests, self).setUp()

        self.base_orm = BaseOrmCallApi()

        # Create organization
        self.post_organization = self.client.post(
            urlhelpers.organization_list_url(), payloads.organization_payload()
        )

    def test_create_organization(self):
        # Test create organization api

        response = self.post_organization
        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], payloads.organization_payload()["name"])

    def test_get_organization(self):
        # Test get organization list api

        response = self.client.get(urlhelpers.organization_list_url())
        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data[0]["name"], payloads.organization_payload()["name"]
        )

    def test_get_organization_detail(self):
        # Test organization detail api

        response = self.client.get(urlhelpers.organization_detail_url())

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["kind"], payloads.organization_payload()["kind"])

    def test_update_organization(self):
        # Test update organization detail api

        payload = {"kind": "kind-elon-updated"}

        response = self.client.patch(urlhelpers.organization_detail_url(), payload)

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["kind"], payload["kind"])

    def test_retrieve_organization_default(self):
        # Test retrieve organization default api

        organization_uid = self.post_organization.data["uid"]

        response = self.client.patch(
            urlhelpers.organization_default_detail_url(organization_uid)
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_organization_info(self):
        # Test retrieve organization information api

        response = self.client.get(urlhelpers.organization_info_detail_url())

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["organization_name"], payloads.organization_payload()["name"]
        )


class PrivateOrganizationUserApiTests(BaseAPITestCase):
    """Test organization user api"""

    def setUp(self):
        super(PrivateOrganizationUserApiTests, self).setUp()

        # Create organization user
        self.post_organization_user = self.client.post(
            urlhelpers.organization_user_list_url(),
            payloads.organization_user_payload(),
        )

        # Get organization user
        self.organization_user = self.client.get(
            urlhelpers.organization_user_list_url()
        )

        # Get organization user uid
        self.organization_user_uid = self.organization_user.data["results"][1]["uid"]

    def test_create_organization_user(self):
        # Test create organization user api

        response = self.post_organization_user

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["phone"], payloads.organization_user_payload()["phone"]
        )

    def test_get_organization_user(self):
        # Test get organzation user list api

        response = self.organization_user

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_get_organization_user_detail(self):
        # Test get organization user detail api

        response = self.client.get(
            urlhelpers.organization_user_detail_url(self.organization_user_uid)
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["role"], payloads.organization_user_payload()["role"]
        )

    def test_update_organization_user(self):
        # Test update organization user api

        # Paylod for test update organization user
        payload = {"role": "ADMIN"}

        response = self.client.patch(
            urlhelpers.organization_user_detail_url(self.organization_user_uid), payload
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], payload["role"])

    def test_delete_organization_user(self):
        # Test delete organization user api

        response = self.client.delete(
            urlhelpers.organization_user_detail_url(self.organization_user_uid)
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class PrivateOrganizationAddressApiTests(BaseAPITestCase):
    """Test organizations address api"""

    def setUp(self):
        super(PrivateOrganizationAddressApiTests, self).setUp()

        self.base_orm = BaseOrmCallApi()

        # Create upazila, district, and division for organization address
        self.division = self.base_orm.division("Dhaka")
        self.district = self.base_orm.district("Gazipur", self.division.name)
        self.upazila = self.base_orm.upazila("Dhamrai", self.district.name)

        # Create organizations address
        self.address = self.client.post(
            urlhelpers.organization_address_url(),
            payloads.organization_address_payload(
                self.upazila.uid, self.district.uid, self.division.uid
            ),
        )


        # Get customer address
        self.get_organization_address = self.client.get(
            urlhelpers.organization_address_url()
        )
        # Get address uid
        self.address_uid = self.get_organization_address.data[0]["uid"]

    def test_create_organization_address(self):
        # Test create organizations address api

        response = self.address
        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["house_street"],
            payloads.organization_address_payload(
                self.upazila.uid, self.district.uid, self.division.uid
            )["house_street"],
        )

    def test_get_organization_address(self):
        # Test get organization address list api

        response = self.client.get(urlhelpers.organization_address_url())

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data[0]["label"],
            payloads.organization_address_payload(
                self.upazila.uid, self.district.uid, self.division.uid
            )["label"],
        )

    def test_get_organization_address_detail(self):
        # Test get organization address detail api

        response = self.client.get(
            urlhelpers.organization_address_detail_url(self.address_uid)
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["country"],
            payloads.organization_address_payload(
                self.upazila.uid, self.district.uid, self.division.uid
            )["country"],
        )

    def test_update_organization_address(self):
        # Test update organization address api

        payload = {"label": "Asad Gate"}

        response = self.client.patch(
            urlhelpers.organization_address_detail_url(self.address_uid), payload
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["label"], payload["label"])

    def test_delete_organization_address(self):
        # Test delete organization address api

        response = self.client.delete(
            urlhelpers.organization_address_detail_url(self.address_uid)
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
