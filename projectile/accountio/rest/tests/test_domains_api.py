from rest_framework import status

from common.base_test import BaseAPITestCase
from weapi.rest.tests import urlhelpers as we_urlhelpers
from ..tests import urlhelpers


class OrganizationDomainApiTests(BaseAPITestCase):
    """Test organization domain availability api"""

    def setUp(self):
        super(OrganizationDomainApiTests, self).setUp()

        # Get organization slug
        self.organization = self.client.get(we_urlhelpers.organization_list_url())
        self.organization_slug = self.organization.data[0]["slug"]

    def test_domain_name_available(self):
        # Test if domain name is available

        response = self.client.get(urlhelpers.organization_domain_url("hello-world"))

        # Assert that the response is correct
        self.assertAlmostEqual(response.status_code, status.HTTP_200_OK)

    def test_domain_name_not_available(self):
        # Test if domain name is not available

        response = self.client.get(
            urlhelpers.organization_domain_url(self.organization_slug)
        )

        # Assert that the response is correct
        self.assertAlmostEqual(response.status_code, status.HTTP_204_NO_CONTENT)
