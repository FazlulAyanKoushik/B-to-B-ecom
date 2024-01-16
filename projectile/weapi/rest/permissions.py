import logging

from rest_framework.permissions import BasePermission

from accountio.models import Organization, OrganizationUser
from accountio.choices import OrganizationUserStatus, OrganizationUserRole
from core.models import User

logger = logging.getLogger(__name__)

permitted_statuses = [
    OrganizationUserStatus.INVITED,
    OrganizationUserStatus.PENDING,
    OrganizationUserStatus.ACTIVE,
    OrganizationUserStatus.HIDDEN,
]


class IsOrganizationCustomer(BasePermission):
    """
    Anyone who works in an organization, whatever his role, can access this normal organization permission.
    Only need to an authorize role of this organization.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        subdomain = request.headers.get("X-DOMAIN", "")
        if len(subdomain) == 0:
            return False

        current_user: User = request.user

        try:
            organization_user = current_user.organizationuser_set.get(
                organization__domain=subdomain
            )
            return organization_user.role == OrganizationUserRole.CUSTOMER
        except OrganizationUser.DoesNotExist:
            logger.warning(f"Cannot find the organizationuser for {current_user}")
            return False


class IsOrganizationOwner(BasePermission):
    """
    Only Owner can access this owner permission
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        try:
            domain = request.headers.get("X-DOMAIN", None)
            organization_user: OrganizationUser = (
                request.user.organizationuser_set.select_related("organization").get(
                    is_default=True
                )
            )
            return (
                organization_user.role == OrganizationUserRole.OWNER
                and organization_user.status in permitted_statuses
                and organization_user.organization.domain == domain
            )
        except:
            return False


class IsOrganizationAdmin(BasePermission):
    """
    Only Owner or Admin can access this admin permission
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        try:
            organization_user = request.user.get_merchent_organization_user()
            return (
                organization_user.role
                in [
                    OrganizationUserRole.OWNER,
                    OrganizationUserRole.ADMIN,
                ]
                and organization_user.status in permitted_statuses
            )
        except:
            return False


class IsOrganizationStaff(BasePermission):
    """
    Owner, Admin or Staff anyone can access this staff permission
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        try:
            domain = request.headers.get("X-DOMAIN", None)
            organization_user: OrganizationUser = (
                request.user.organizationuser_set.select_related("organization").get(
                    is_default=True
                )
            )
            return (
                organization_user.role
                in [
                    OrganizationUserRole.OWNER,
                    OrganizationUserRole.ADMIN,
                    OrganizationUserRole.STAFF,
                    OrganizationUserRole.MANAGER,
                ]
                and organization_user.status in permitted_statuses
                and organization_user.organization.domain == domain
            )
        except:
            return False


class IsOrganizationManager(BasePermission):
    """
    Owner, Admin or Manager anyone can access this manager permission
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        try:
            organization_user = request.user.get_merchent_organization_user()
            return (
                organization_user.role
                in [
                    OrganizationUserRole.OWNER,
                    OrganizationUserRole.ADMIN,
                    OrganizationUserRole.MANAGER,
                ]
                and organization_user.status in permitted_statuses
            )
        except:
            return False
