from django.urls import path

from ..views.inbox import (
    PrivateOrganizationThreadList,
    PrivateOrganizationThreadReplyList,
)


urlpatterns = [
    path(
        r"/<uuid:uid>",
        PrivateOrganizationThreadReplyList.as_view(),
        name="we.organization-thread-reply",
    ),
    path(
        r"",
        PrivateOrganizationThreadList.as_view(),
        name="we.organization-thread-list",
    ),
]