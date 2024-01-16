from django.urls import reverse


def user_registration_list_url():
    return reverse("user-registration")


def user_password_reset_url():
    return reverse("password_reset")


def user_token_login_url():
    return reverse("token_obtain_pair")


def organization_register_list_url():
    return reverse("organization.registration")


def me_detail_url():
    return reverse("me-detail")


def organization_user_list_url():
    return reverse("organization-user-list")


def organization_user_detail_url(uid):
    return reverse("organization-user-detail", args=[uid])


def me_organization_select_url(uid):
    return reverse("me-organization-set-default", args=[uid])


def organization_list_url():
    return reverse("organization-list")
