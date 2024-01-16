import decimal

from django.contrib.auth import get_user_model

from accountio.models import OrganizationUser

User = get_user_model()


def add_customer_extra_role_balance_information(
    user: User,
    organization_user: OrganizationUser,
    total_pay: decimal.Decimal,
    total_buy: decimal.Decimal,
) -> User:
    # set the extra information to user object
    user.total_orders = user.orders.count()
    user.discount_offset = organization_user.discount_offset
    user.role = organization_user.role
    user.total_payable = total_pay
    user.total_buying = total_buy
    user.balance = total_pay - total_buy

    return user
