import csv
import io
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status

from accountio.models import Organization

from catalogio.models import Product, Manufacturer, DosageForm

from common.base_orm import BaseOrmCallApi
from common.base_test import BaseAPITestCase

from core.models import User

from . import payloads, urlhelpers


class PrivateProductApiTests(BaseAPITestCase):
    """Test products api"""

    def setUp(self):
        super(PrivateProductApiTests, self).setUp()

        self.base_orm = BaseOrmCallApi()

        # Create base product
        self.base_product = self.base_orm.baseproduct(payloads.base_product_payload())

        # Get base product uid
        self.base_product_uid = self.base_product.uid

        # Get organization
        self.organization = self.client.get(urlhelpers.organization_list_url())

        # Get organization user uid
        self.user = self.client.get(urlhelpers.organization_user_list_url())
        self.user_uid = self.user.data["results"][0]["user"]["uid"]
        self.organization_name = self.organization.data[0]["name"]

        # Create product payload
        self.payload = {
            "base_product": self.base_product_uid,
            "organization": self.organization,
            "stock": 10,
            "selling_price": "100",
            "merchant": self.user_uid,
            "tag_names": ["orange", "green"],
        }

        # Create product
        self.post_response = self.client.post(
            urlhelpers.product_list_url(), self.payload
        )

        # Assert that the response is correct
        self.assertEqual(self.post_response.status_code, status.HTTP_201_CREATED)

        # Get product uid
        self.product_uid = self.post_response.data["uid"]


    def test_create_product(self):
        # Test create product api

        response = self.post_response

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["stock"], self.payload["stock"])
        self.assertEqual(len(response.data["tags"]), 2)

    def test_get_product(self):
        # Test get product list api

        response = self.client.get(urlhelpers.product_list_url())

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_retrieve_product(self):
        # Test retrieve product detail api

        response = self.client.get(urlhelpers.product_detail_url(self.product_uid))

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["stock"], self.payload["stock"])

    def test_update_product(self):
        # Test update product api

        # Payload for update
        payload = {"stock": 20}

        response = self.client.patch(
            urlhelpers.product_detail_url(self.product_uid), payload
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["stock"], payload["stock"])

    def test_delete_product(self):
        # Test delete product api

        response = self.client.delete(urlhelpers.product_detail_url(self.product_uid))

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_product_bulk_discount(self):
        # Test bulk discount update api

        organization = Organization.objects.get(name=self.organization_name)
        merchant = User.objects.get(uid=self.user_uid)

        # Creating some products
        product_one = Product.objects.create(
            base_product=self.base_product,
            organization=organization,
            stock=100,
            merchant=merchant,
            discount_price=100,
        )
        product_two = Product.objects.create(
            base_product=self.base_product,
            organization=organization,
            stock=90,
            merchant=merchant,
            discount_price=100,
        )
        product_three = Product.objects.create(
            base_product=self.base_product,
            organization=organization,
            stock=80,
            merchant=merchant,
            discount_price=100,
        )
        product_list = [product_one.uid, product_two.uid, product_three.uid]

        response = self.client.put(
            urlhelpers.bulk_discount_update_url(),
            {
                "products": product_list,
                "manufacturer": Manufacturer.objects.create(name="Beximco").uid,
                "dosage_form": DosageForm.objects.create(name="oral").uid,
                "discount_percent": Decimal(20.0),
            },
        )
        product_one.refresh_from_db()
        product_two.refresh_from_db()
        product_three.refresh_from_db()
        self.assertEqual(product_one.discount_price, Decimal(100.0))
        self.assertEqual(product_two.discount_price, Decimal(100.0))
        self.assertEqual(product_three.discount_price, Decimal(100.0))

    def test_product_out_of_stock(self):
        # Test product_out_of_stock api
        organization = Organization.objects.get(name=self.organization_name)
        merchant = User.objects.get(uid=self.user_uid)

        # Creating some products
        product_one = Product.objects.create(
            base_product=self.base_product,
            organization=organization,
            stock=0,
            merchant=merchant,
            discount_price=100,
        )
        product_two = Product.objects.create(
            base_product=self.base_product,
            organization=organization,
            stock=0,
            merchant=merchant,
            discount_price=100,
        )
        product_three = Product.objects.create(
            base_product=self.base_product,
            organization=organization,
            stock=1,
            merchant=merchant,
            discount_price=100,
        )

        response = self.client.get(urlhelpers.product_out_of_stock_url())
        self.assertEqual(response.data["count"], 2)

    def test_product_bulk_download(self):
        # Test product bulk download api
        organization = Organization.objects.get(name=self.organization_name)
        merchant = User.objects.get(uid=self.user_uid)

        # Creating some products
        product_one = Product.objects.create(
            base_product=self.base_product,
            organization=organization,
            stock=100,
            merchant=merchant,
            discount_price=100,
        )
        product_two = Product.objects.create(
            base_product=self.base_product,
            organization=organization,
            stock=90,
            merchant=merchant,
            discount_price=100,
        )
        product_three = Product.objects.create(
            base_product=self.base_product,
            organization=organization,
            stock=80,
            merchant=merchant,
            discount_price=100,
        )

        response = self.client.get(urlhelpers.product_bulk_download_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_product_bulk_update(self):
    #     # Test product bulk update api
    #     organization = Organization.objects.get(name=self.organization_name)
    #     merchant = User.objects.get(uid=self.user_uid)

    #     # Creating some products
    #     product_one = Product.objects.create(
    #         base_product=self.base_product,
    #         organization=organization,
    #         stock=100,
    #         merchant=merchant,
    #         discount_price=100,
    #     )
    #     product_two = Product.objects.create(
    #         base_product=self.base_product,
    #         organization=organization,
    #         stock=90,
    #         merchant=merchant,
    #         discount_price=100,
    #     )
    #     product_three = Product.objects.create(
    #         base_product=self.base_product,
    #         organization=organization,
    #         stock=80,
    #         merchant=merchant,
    #         discount_price=100,
    #     )

    #     response = self.client.get(urlhelpers.product_bulk_download_url())
    #     content = response.content
    #     csv_file = io.StringIO(content.decode("utf-8"))
    #     csv_reader = csv.reader(csv_file)
    #     rows = list(csv_reader)
    #     rows[1][3] = Decimal(200)
    #     rows[1][5] = 20

    #     updated_csv_file = io.StringIO()
    #     csv_writer = csv.writer(updated_csv_file)
    #     csv_writer.writerows(rows)

    #     file = SimpleUploadedFile(
    #         "test.xlsx", updated_csv_file.getvalue().encode("utf-8")
    #     )
    #     response = self.client.put(urlhelpers.product_bulk_update_url(), {"file": file})

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     product_one.refresh_from_db()
    #     product_two.refresh_from_db()
    #     product_three.refresh_from_db()

    #     response = self.client.get(urlhelpers.product_bulk_download_url())

    #     content = response.content
    #     csv_file = io.StringIO(content.decode("utf-8"))
    #     csv_reader = csv.reader(csv_file)
    #     rows = list(csv_reader)
    #     self.assertEqual(Decimal(rows[1][3]), Decimal(200))
