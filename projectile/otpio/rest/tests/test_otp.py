# from django.contrib.auth import get_user_model
# from rest_framework import status
# from rest_framework.test import APIClient, APITestCase

# from core.rest.tests import urlhelpers, payloads
# from otpio.models import UserPhoneOTP
# from .urlhelpers import verify_otp_url, resend_otp_url

# User = get_user_model()


# class PublicOTPTestCase(APITestCase):
#     """Public Test Case for OTP"""

#     def setUp(self):
#         self.client = APIClient()

#         # Create organization
#         self.create_organization = self.client.post(
#             urlhelpers.organization_register_list_url(),
#             payloads.organization_registration_payload(),
#         )

#         # Logged in organization user
#         self.user_login = self.client.post(
#             urlhelpers.user_token_login_url(),
#             payloads.organization_user_login_payload(),
#         )

#         self.client.credentials(
#             HTTP_AUTHORIZATION="Bearer " + self.user_login.data["access"],
#             HTTP_X_DOMAIN="zakir-corp",
#         )

#     def test_otp_verify(self):
#         # Test OTP verify successfully

#         # Create a user using API
#         response_user = self.client.post(
#             urlhelpers.user_registration_list_url(),
#             payloads.user_registration_payload(),
#         )

#         # Get a user object by phone number
#         user = User.objects.get(phone=response_user.data["phone"])
#         # Get a User phone otp
#         user_phone_otp = UserPhoneOTP.objects.get(user=user)
#         # Creating payload for verify otp
#         payload = {"otp": user_phone_otp.otp}

#         response = self.client.put(verify_otp_url(), payload)

#         # Assert that the response is correct
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         # Asserts that the response containing access and refresh token
#         self.assertTrue("access" in response.data)
#         self.assertTrue("refresh" in response.data)

#     def test_resend_otp(self):
#         # Test resend otp successfully

#         # Create a user using API
#         response_user = self.client.post(
#             urlhelpers.user_registration_list_url(),
#             payloads.user_registration_payload(),
#         )

#         # Get a user object by phone number
#         user = User.objects.get(phone=response_user.data["phone"])

#         # Creating payload for verify otp
#         payload = {"phone": response_user.data["phone"]}

#         response = self.client.post(resend_otp_url(), payload)

#         # Assert that the response is correct
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
