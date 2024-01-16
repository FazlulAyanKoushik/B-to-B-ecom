from django.urls import path

from ..views import customers

urlpatterns = [
    path(
        "/orders",
        customers.PrivateCustomerOrderList.as_view(),
        name="customer-order-list",
    ),
    path(
        "/orders/<uuid:uid>",
        customers.PrivateCustomerOrderDetail.as_view(),
        name="customer-order-detail",
    ),
    # path(
    #     "/<uuid:uid>/order-analytics/<int:year>",
    #     customers.PrivateCustomerCountByMonthOfAYear.as_view(),
    #     name="organization-customer-order-count-by-month-of-a-year",
    # ),
    # path(
    #     "/<uuid:uid>/order-analytics",
    #     customers.PrivateCustomerOrderCount.as_view(),
    #     name="organization-customer-order-analytics",
    # ),
    path(
        "/transactions",
        customers.PrivateCustomerTransactionHistory.as_view(),
        name="customer-transactions",
    ),
    path(
        "/<uuid:uid>",
        customers.PrivateCustomerDetail.as_view(),
        name="organization-customer-detail",
    ),
    path(
        "",
        customers.PrivateCustomerList.as_view(),
        name="organization-customer-list",
    ),
]
