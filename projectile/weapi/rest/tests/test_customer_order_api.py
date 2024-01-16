import datetime

from django.contrib.auth import get_user_model

from rest_framework import status

from accountio.choices import OrganizationUserRole, OrganizationUserStatus
from accountio.models import Organization, OrganizationUser, TransactionOrganizationUser

from catalogio.rest.tests import urlhelpers as catalogio_urlhelpers

from common.base_orm import BaseOrmCallApi
from common.base_test import BaseAPITestCase

from core.rest.tests import urlhelpers as core_urlhelpers

from orderio.choices import OrderDeliveryStatus, OrderStageChoices

from . import payloads, urlhelpers


User = get_user_model()


class PrivateCustomersOrderListApiTests(BaseAPITestCase):
    """Test organization customer order list api"""

    def setUp(self):
        super(PrivateCustomersOrderListApiTests, self).setUp()

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
            "discount_price": "50",
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

        # Assert that the response is correct
        self.assertEqual(self.customer.status_code, status.HTTP_201_CREATED)

        # Logged in customer
        self.customer_login = self.client.post(
            core_urlhelpers.user_token_login_url(), payloads.customer_login_payload()
        )

        # Provide customer credentials for accessing restricted api
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + self.customer_login.data["access"],
            HTTP_X_DOMAIN="bill-corp",
        )

        # Create upazila, district, and division for customer address
        self.division = self.base_orm.division("Dhaka")
        self.district = self.base_orm.district("Gazipur", self.division.name)
        self.upazila = self.base_orm.upazila("Dhamrai", self.district.name)

        # Create customer address
        self.address = self.client.post(
            urlhelpers.create_customer_address_url(),
            payloads.customer_address_payload(
                self.upazila.uid, self.district.uid, self.division.uid
            ),
        )

        # Get address uid for orders
        self.get_address = self.client.get(urlhelpers.create_customer_address_url())
        self.address_uid = self.get_address.data[0]["uid"]

        # Payment method slug
        self.payment_method = self.base_orm.payment_method()
        self.payment_uid = self.payment_method.uid

        # Add product on cart
        self.product = self.client.post(
            urlhelpers.cart_products_list_url(),
            payloads.add_product_payload(self.product_slug),
        )

        # Assert that the response is correct
        self.assertEqual(self.product.status_code, status.HTTP_201_CREATED)

        # Place order from customer side
        self.create_order_list = self.client.post(
            urlhelpers.create_order_list_url(),
            payloads.customer_order_payload(self.address_uid, self.payment_uid),
        )

        # Get customer order list & uid
        self.get_order_list = self.client.get(urlhelpers.create_order_list_url())
        self.customer_order_uid = self.get_order_list.data["results"][0]["uid"]

    def test_get_customer_order_list(self):
        # Test get organization customer order list api

        response = self.get_order_list

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_customer_order(self):
        # Test create customer order list api

        response = self.create_order_list

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["products"][0]["quantity"],
            payloads.add_product_payload(self.product_slug)["quantity"],
        )

    def test_get_customer_order_detail(self):
        # Test get organization customer order detail api

        response = self.client.get(
            urlhelpers.customer_order_detail_url(self.customer_order_uid)
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["products"][0]["quantity"],
            payloads.add_product_payload(self.product_slug)["quantity"],
        )

    def test_delivery_charge(self):
        # Test retrieve delivery charge by address uid
        user = User.objects.get(uid=self.user_uid)
        self.delivery_charge_payload = {
            "charge": "50.00",
            "district": self.district,
            "admin": user,
        }
        self.delivery_charge = self.base_orm.delivery_charge(
            self.delivery_charge_payload
        )
        response = self.client.get(
            urlhelpers.customer_delivery_charge_detail(self.address_uid)
        )
        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert that the response charge is 50
        self.assertEqual(
            response.data["charge"], self.delivery_charge_payload["charge"]
        )


class OrganizationStaffCustomersOrderListApiTests(BaseAPITestCase):
    """Test for organization stuff customer orders api"""

    def setUp(self):
        super(OrganizationStaffCustomersOrderListApiTests, self).setUp()
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
            "discount_price": "50",
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

        # Assert that the response is correct
        self.assertEqual(self.customer.status_code, status.HTTP_201_CREATED)

        self.get_customer_list = self.client.get(
            urlhelpers.organization_customer_list_url()
        )

        # Create upazila, district, and division for customer address
        self.division = self.base_orm.division("Dhaka")
        self.district = self.base_orm.district("Gazipur", self.division.name)
        self.upazila = self.base_orm.upazila("Dhamrai", self.district.name)

        # Create customer address
        self.address = self.client.post(
            urlhelpers.create_customer_address_url(),
            payloads.customer_address_payload(
                self.upazila.uid, self.district.uid, self.division.uid
            ),
        )

        # Get address uid for orders
        self.get_address = self.client.get(urlhelpers.create_customer_address_url())
        self.address_uid = self.get_address.data[0]["uid"]

        # Payment method slug
        self.payment_method = self.base_orm.payment_method()
        self.payment_uid = self.payment_method.uid

        # Add product on cart
        self.product = self.client.post(
            urlhelpers.cart_products_list_url(),
            payloads.add_product_payload(self.product_slug),
        )

        # Assert that the response is correct
        self.assertEqual(self.product.status_code, status.HTTP_201_CREATED)

        # Place order from customer side
        self.create_order_list = self.client.post(
            urlhelpers.create_order_list_url(),
            payloads.customer_order_payload(self.address_uid, self.payment_uid),
        )
        self.order_status = OrderDeliveryStatus
        self.order_stage = OrderStageChoices
        self.user_role = OrganizationUserRole
        self.organization_user_status = OrganizationUserStatus

        # Get customer order list & uid
        self.get_order_list = self.client.get(urlhelpers.create_order_list_url())
        self.customer_order_uid = self.get_order_list.data["results"][0]["uid"]

    def test_private_customer_list(self):
        # Test for Retrieving all private customer lists for an organization
        response = self.client.get(urlhelpers.organization_customer_list_url())

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert that the result has in response
        self.assertTrue("results" in response.data)

    def test_customer_detail(self):
        # Test for get a customer detail who buys products from merchant organization.
        response = self.client.get(
            urlhelpers.organization_customer_detail_url(
                self.get_customer_list.data["results"][0]["uid"]
            )
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_update_api(self):
        # test customer discount offset update by from merchant organization.
        payload = {
            "discount_offset": 10,
        }
        response = self.client.patch(
            urlhelpers.organization_customer_detail_url(
                self.get_customer_list.data["results"][0]["uid"]
            ),
            payload,
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert that customer discount offset is the same as payload
        self.assertEqual(response.data["discount_offset"], 10)

    def test_order_count_by_all_current_status_of_merchant_customer(self):
        # Test retrieve order count by all delivery statuses of merchant customer

        new_customer = self.base_orm.create_user(
            phone="+8801722222244",
            password="newpass1122",
            **payloads.user_naming_payload()
        )
        organization = Organization.objects.get(uid=self.organization.data[0]["uid"])
        organization_user = self.base_orm.create_organization_user(
            organization=organization,
            user=new_customer,
            role=self.user_role.CUSTOMER,
        )
        organization_user.save()

        payment_method = self.base_orm.payment_method()

        address = payloads.address_payload()

        order1 = self.base_orm.create_order(
            customer=new_customer,
            organization=organization,
            order_by=new_customer,
            total_price="200.00",
            address=address,
            payment_method=payment_method,
        )
        order2 = self.base_orm.create_order(
            customer=new_customer,
            organization=organization,
            order_by=new_customer,
            total_price="300.00",
            address=address,
            payment_method=payment_method,
        )
        order_delivery1 = self.base_orm.create_order_delivery(
            status=self.order_status.ORDER_PLACED,
            stage=self.order_stage.CURRENT,
            order=order1,
        )
        order_delivery2 = self.base_orm.create_order_delivery(
            status=self.order_status.ORDER_PLACED,
            stage=self.order_stage.CURRENT,
            order=order2,
        )

        response = self.client.get(
            urlhelpers.private_customer_order_count_url(new_customer.uid)
        )

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert that the response is correct which I'm expecting
        self.assertEqual(
            response.data["order_count_by_status"][0]["total_order_count"], 2
        )

    def test_customer_order_transaction_api(self):
        # Test transactions of customer's orders
        customer = self.base_orm.get_user("+8801711112222")

        organization = Organization.objects.get(uid=self.organization.data[0]["uid"])
        organization_user = self.base_orm.create_organization_user(
            organization=organization,
            user=customer,
            role=self.user_role.CUSTOMER,
        )
        organization_user.save()

        payment_method = self.base_orm.payment_method()

        address = payloads.address_payload()

        order1 = self.base_orm.create_order(
            customer=customer,
            organization=organization,
            order_by=customer,
            total_price="2000.00",
            address=address,
            payment_method=payment_method,
        )

        order2 = self.base_orm.create_order(
            customer=customer,
            organization=organization,
            order_by=customer,
            total_price="5000.00",
            address=address,
            payment_method=payment_method,
        )

        transaction1 = self.base_orm.create_transaction(
            organization=organization,
            user=customer,
            order=order1,
            total_money="2000.00",
            payable_money="2000.00",
        )

        transaction2 = self.base_orm.create_transaction(
            organization=organization,
            user=customer,
            order=order2,
            total_money="5000.00",
            payable_money="5000.00",
        )

        response = self.client.get(urlhelpers.private_customer_order_transactions())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_money"], "7000.00")
