from rest_framework import status

from common.base_test import BaseAPITestCase
from common.base_orm import BaseOrmCallApi

from . import payloads, urlhelpers


class PrivateTagApiTest(BaseAPITestCase):
    def setUp(self):
        super(PrivateTagApiTest, self).setUp()

        self.base_orm = BaseOrmCallApi()

        # create tag
        self.tag_post_response = self.client.post(
            urlhelpers.tag_list_url(), payloads.tag_payload()
        )

        self.assertEqual(self.tag_post_response.status_code, status.HTTP_201_CREATED)

        # get tag uid
        self.tag_uid = self.tag_post_response.data["uid"]

    def test_create_tag(self):
        # Test for create tag

        response = self.tag_post_response

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], payloads.tag_payload()["name"])

    def test_get_tag(self):
        # Test for tag list

        response = self.client.get(urlhelpers.tag_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_retrieve_tag(self):
        # Test for retrieve tag detail

        response = self.client.get(urlhelpers.tag_detail_url(self.tag_uid))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uid"], self.tag_uid)

    def test_update_tag(self):
        # Test for update tag

        payload = {"name": "Update-tag_1"}

        response = self.client.patch(urlhelpers.tag_detail_url(self.tag_uid), payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], payload["name"])

    def test_delete_tag(self):
        # Test for delete tag

        response = self.client.delete(urlhelpers.tag_detail_url(self.tag_uid))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
