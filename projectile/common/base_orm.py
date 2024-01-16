import logging

from rest_framework.test import APITestCase

from accountio.choices import OrganizationUserStatus
from accountio.models import OrganizationUser, Organization, TransactionOrganizationUser

from addressio.models import (
    User,
    Upazila,
    District,
    Division,
)

from catalogio.models import (
    Brand,
    DosageForm,
    Ingredient,
    Manufacturer,
    Supplier,
    MedicinePhysicalState,
    RouteOfAdministration,
    BaseProduct,
    Category,
    DeliveryCharge,
)

from orderio.models import Order, OrderDelivery

from paymentio.models import PaymentMethod

logger = logging.getLogger(__name__)
logger.warning("We are calling orm calls here but we do not like it")


class BaseOrmCallApi(APITestCase):
    # create superuser
    def super_user(self):
        return User.objects.create_superuser(
            first_name="Joee",
            last_name="Baidene",
            phone="+8801788888888",
            password="new123pass",
        )

    # create user
    def new_user(self):
        return User.objects.create(phone="+8801722222222", password="new123pass")

    def get_user(self, phone: str):
        return User.objects.get(phone=phone)

    # create category
    def category(self):
        return Category.objects.create(name="Injection")

    # create brand
    def brand(self):
        return Brand.objects.create(name="Eximco")

    # create dosage form
    def dosage_form(self):
        return DosageForm.objects.create(name="Dosage_1")

    # create ingredient
    def ingredient(self):
        return Ingredient.objects.create(name="Minoxidil")

    # create manufacturer
    def manufacturer(self):
        return Manufacturer.objects.create(name="Manufacturers1")

    # create supplier
    def supplier(self):
        return Supplier.objects.create(name="Suppliers1")

    # create medicinephysicalstate
    def medicine_physical_state(self):
        return MedicinePhysicalState.objects.create(name="medicinePhysicalStates1")

    # create routeofadministration
    def route_of_administration(self):
        return RouteOfAdministration.objects.create(name="RouteOfAdministrations1")

    # create upazila
    def upazila(self, upazila_name, district_name=None):
        district, _ = District.objects.get_or_create(name=district_name)
        division = Division.objects.create(name="Dhaka")
        return Upazila.objects.create(
            name=upazila_name, district=district, division=division
        )

    # create district
    def district(self, district_name, division_name=None):
        division, _ = Division.objects.get_or_create(name=division_name)
        return District.objects.create(name=district_name, division=division)

    # create division
    def division(self, division_name):
        return Division.objects.create(name=division_name)

    # create payment method
    def payment_method(self):
        return PaymentMethod.objects.create(name="Cash on Delivery")

    # create baseproduct
    def baseproduct(self, kwargs):
        base_product = BaseProduct.objects.create(
            superadmin=kwargs.get("superadmin"),
            name="Napa",
            dosage_form=kwargs.get("dosage_form"),
            manufacturer=kwargs.get("manufacturer"),
            unit=kwargs.get("unit"),
            brand=kwargs.get("brand"),
            category=kwargs.get("category"),
            route_of_administration=kwargs.get("route_of_administration"),
            medicine_physical_state=kwargs.get("medicine_physical_state"),
        )

        base_product.active_ingredients.add(kwargs.get("ingredient"))

        return base_product

    # delivery charge
    def delivery_charge(self, payload):
        return DeliveryCharge.objects.create(
            charge=payload["charge"],
            district=payload["district"],
            admin=payload["admin"],
        )

    def create_order(self, **payload):
        return Order.objects.create(**payload)

    def create_order_delivery(self, **payload):
        return OrderDelivery.objects.create(**payload)

    def create_organization(self, name: str) -> Organization:
        organization, _ = Organization.objects.get_or_create(name=name)
        return organization

    def create_organization_user(
        self, organization: Organization, user: User, role, is_default=True
    ) -> OrganizationUser:
        organization_user, _ = OrganizationUser.objects.get_or_create(
            organization=organization,
            user=user,
            defaults={
                "role": role,
                "is_default": is_default,
                "status": OrganizationUserStatus.ACTIVE,
            },
        )
        return organization_user

    def create_user(self, phone="+8801722222244", password="newpass123", **kwargs):
        return User.objects.create(phone=phone, password=password, **kwargs)

    def create_transaction(
        self,
        organization: Organization,
        user: User,
        order: Order,
        total_money="1000.00",
        payable_money="1000.00",
    ):
        return TransactionOrganizationUser.objects.create(
            organization=organization,
            user=user,
            order=order,
            total_money=total_money,
            payable_money=payable_money,
        )
