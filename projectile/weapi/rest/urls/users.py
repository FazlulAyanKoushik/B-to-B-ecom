from django.urls import path

from ..views import users

urlpatterns = [
    path(
        "/<uuid:customer_uid>/order-analytics",
        users.PrivateCustomerOrderCount.as_view(),
        name="organization-customer-order-analytics",
    ),
    path(
        "/<uuid:customer_uid>/order-analytics/<int:year>",
        users.PrivateCustomerCountByMonthOfAYear.as_view(),
        name="organization-customer-order-count-by-month-of-a-year",
    ),
    path(
        "/<uuid:uid>/transactions",
        users.PrivateCustomerTransactionHistoryList.as_view(),
        name="organization-user-transaction-history",
    ),
    path(
        "/<uuid:user_uid>",
        users.PrivateOrganizationUserDetail.as_view(),
        name="organization-user-detail",
    ),
    path(
        "",
        users.PrivateOrganizationUserList.as_view(),
        name="organization-user-list",
    ),
]
