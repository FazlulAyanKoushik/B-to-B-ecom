from django.urls import path

from ..views import me

urlpatterns = [
    path(
        "/organizations",
        me.PrivateOrganizationUserList.as_view(),
        name="organization-user-list",
    ),
    path(
        r"/organizations/<uuid:uid>",
        me.PrivateOrganizationUserDetail.as_view(),
        name="organization-user-detail",
    ),
    path(
        "/organizations/<str:organization_slug>/select",
        me.PrivateOrganizationDefaultDetail.as_view(),
        name="me-organization-set-default",
    ),
    path(
        "/notifications",
        me.PrivateNotificationList.as_view(),
        name="me-notifications-list",
    ),
    path(
        "/notifications/count",
        me.PrivateNotificationCountDetail.as_view(),
        name="me-notifications-count-detail",
    ),
    path(
        "/notifications/seen/all",
        me.PrivateNotificationSeenAllDetail.as_view(),
        name="me-notifications-seen-all",
    ),
    path(
        "/notifications/<uuid:uid>/seen",
        me.PrivateNotificationDetail.as_view(),
        name="me-notifications-detail",
    ),
    path(
        "/inbox",
        me.PrivateThreadList.as_view(),
        name="thread-list",
    ),
    path(
        "/inbox/<uuid:uid>",
        me.PrivateThreadReplyList.as_view(),
        name="thread-reply-list",
    ),
    path(
        "",
        me.PrivateMeDetail.as_view(),
        name="me-detail",
    ),
]
