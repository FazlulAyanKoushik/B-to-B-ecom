import logging

from rest_framework import status

from accountio.choices import OrganizationUserRole

from common.base_test import BaseAPITestCase
from common.base_orm import BaseOrmCallApi

from weapi.rest.tests import payloads as we_payloads

from . import payloads, urlhelpers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PrivateMeApiTests(BaseAPITestCase):
    """Test for private me api"""

    def setUp(self):
        super(PrivateMeApiTests, self).setUp()

        self.base_orm = BaseOrmCallApi()

        # Onboarding organization with user
        self.create_orgganization_onboard = self.client.post(
            urlhelpers.organization_user_list_url(),
            payloads.organization_user_payload(),
        )

        # Assert that the response is correct
        self.assertEqual(
            self.create_orgganization_onboard.status_code, status.HTTP_201_CREATED
        )

        # Get organization user list
        self.organization_user = self.client.get(
            urlhelpers.organization_user_list_url()
        )
        # Organization user uid
        self.organization_uid = self.organization_user.data["results"][1]["uid"]

    def test_retrieve_me(self):
        # Get merchant user detail

        response = self.client.get(urlhelpers.me_detail_url())
        logger.info(" Currnet User Detail")

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["phone"], we_payloads.user_and_organization_payload()["phone"]
        )

    def test_update_me(self):
        # Test for updating me

        payload = {"first_name": "abc updated name"}
        response = self.client.patch(urlhelpers.me_detail_url(), payload)
        logger.info(" Updated Current User Detail")

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], payload["first_name"])

    def test_merchant_user_list(self):
        # Organization user list

        response = self.client.get(urlhelpers.organization_user_list_url())

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_retrieve_merchant_user(self):
        # Single instance retrieve

        response = self.client.get(
            urlhelpers.organization_user_detail_url(self.organization_uid)
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_merchant_user(self):
        # Organization user update only 'role and status'

        # Payload for updating organization user role
        payload = {"role": "ADMIN"}

        response = self.client.patch(
            urlhelpers.organization_user_detail_url(self.organization_uid),
            payload,
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], payload["role"])

    def test_delete_merchat_user(self):
        # Delete Organization User Using Onboarding RetrieveUpdateDestroyView

        response = self.client.delete(
            urlhelpers.organization_user_detail_url(self.organization_uid)
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        logger.info("No orm calls, pure rest tests.")

    def test_set_default_organizatio_user(self):
        # Test set default organization user api

        response = self.client.patch(
            urlhelpers.organization_user_detail_url(self.organization_uid),
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_organization_user(self):
        # creating organization with user me_detail_url
        user = self.base_orm.get_user("+8801711112222")

        organization_1 = self.base_orm.create_organization("mirpur pharma")
        create_org_user_1 = self.base_orm.create_organization_user(
            organization=organization_1,
            user=user,
            role=OrganizationUserRole.ADMIN,
            is_default=False,
        )

        organization_2 = self.base_orm.create_organization("bill crop")
        create_org_user_2 = self.base_orm.create_organization_user(
            organization=organization_2,
            user=user,
            role=OrganizationUserRole.ADMIN,
        )

        response = self.client.patch(
            urlhelpers.me_organization_select_url(organization_1.uid),
        )

        current_organization = self.client.get(urlhelpers.organization_list_url())

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert that the response is correct which I'm expecting
        self.assertEqual(current_organization.data[0]["domain"], organization_1.domain)
