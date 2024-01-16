from django.urls import path

from ..views.dashboards import PrivateDashboardList

urlpatterns = [
    path(r"", PrivateDashboardList.as_view(), name="dashboard-list"),
]
