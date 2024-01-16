from django.contrib.auth.hashers import make_password
from django.core.management import BaseCommand, call_command

from accountio.choices import OrganizationUserRole
from accountio.models import Organization, OrganizationUser

from core.models import User

from paymentio.models import PaymentMethod


def add_user(first_name, last_name, phone, password, is_admin=False) -> User:
    if is_admin:
        return User.objects.create_superuser(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            password=password,
        )
    else:
        return User.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            password=make_password(password),
        )


def add_user_to_organization(
    user: User,
    organization: Organization,
    role=OrganizationUserRole.STAFF,
    is_default=True,
):
    OrganizationUser.objects.create(
        user=user, organization=organization, role=role, is_default=is_default
    )


class Command(BaseCommand):
    def handle(self, *args, **options):
        mirpur_pharma = Organization.objects.create(name="mirpur pharma")

        bappi = add_user(
            first_name="AB",
            last_name="Bappi",
            phone="+8801309192698",
            password="bappi",
            is_admin=True,
        )
        add_user_to_organization(
            user=bappi, organization=mirpur_pharma, role=OrganizationUserRole.ADMIN
        )
        self.stdout.write("Bappi -> SUPER_USER -> ADMIN")

        saif = add_user(
            first_name="Saifullah",
            last_name="Shahen",
            phone="+8801752495467",
            password="123456",
            is_admin=True,
        )
        add_user_to_organization(
            user=saif, organization=mirpur_pharma, role=OrganizationUserRole.ADMIN
        )
        self.stdout.write("Shahen -> SUPER_USER -> ADMIN")

        shamim_merchant = add_user(
            first_name="Shamim",
            last_name="Bin Zahid",
            phone="+8801681845722",
            password="123456789",
            is_admin=True,
        )
        add_user_to_organization(
            user=shamim_merchant,
            organization=mirpur_pharma,
            role=OrganizationUserRole.ADMIN,
        )
        self.stdout.write("Shamim -> SUPER_USER -> ADMIN")

        muntashir_customer = add_user(
            first_name="Muntashir",
            last_name="Wahid",
            phone="+8801703607476",
            password="123456789",
        )
        add_user_to_organization(
            user=muntashir_customer,
            organization=mirpur_pharma,
            role=OrganizationUserRole.CUSTOMER,
            is_default=False,
        )
        self.stdout.write("Muntashir -> CUSTOMER")

        sazzad_merchant = add_user(
            first_name="Sazzad",
            last_name="Islam",
            phone="+8801755972190",
            password="123456789",
        )
        add_user_to_organization(
            user=sazzad_merchant,
            organization=mirpur_pharma,
            role=OrganizationUserRole.ADMIN,
        )
        self.stdout.write("Sazzad -> ADMIN")
        self.stdout.write("..............................................\n")

        self.stdout.write("Loading Address data ...")
        call_command("loadaddressdata")

        self.stdout.write("..............................................\n")
        self.stdout.write("Creating cash on delivery ...")
        PaymentMethod.objects.create(name="cash on delivery")

        self.stdout.write(".............................................. \n")
        self.stdout.write("Loading base product ...")
        call_command("loadbaseproduct")
