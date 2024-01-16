import os
import re
from typing import List

from infobip_channels.sms.channel import SMSChannel
from rest_framework.exceptions import ValidationError


class SMS:
    _BASE_URL = "https://jdyvkv.api.infobip.com"

    def __init__(self):
        self._channel = SMSChannel.from_auth_params(
            {
                "base_url": self._BASE_URL,
                "api_key": os.environ.get("INFOBIP_APIKEY"),
            }
        )

    def send_otp(self, recipients: List[str], otp: str) -> bool | ValidationError:
        """
        @recipients add numbers of the users like 8801681845722.
        @message write message for the recipient users.
        Response will be true if sms response is 200.
        """

        # validation number
        for index, _ in enumerate(recipients):
            # Checking number using regex if number is Bangladeshi
            pattern = r"^(((\+)?880))(\d){10}$"
            try:
                regex_validator = re.compile(pattern, re.I)
            except re.error:
                raise ValidationError({"detail": "Invalid regex pattern"})
            if not regex_validator.match(recipients[index]):
                raise ValidationError(
                    {
                        "detail": "Invalid phone number. Accepted numbers are 8801681845722 or +8801681845722"
                    }
                )

            # remove + from the start of the number if exists
            if recipients[index].startswith("+"):
                recipients[index] = recipients[index][1:]

        # sending sms to phone numbers
        response = self._channel.send_sms_message(
            {
                "messages": [
                    {
                        "destinations": [{"to": number} for number in recipients],
                        "text": f"Your REPLIQ OTP is {otp}. Thanks",
                    }
                ]
            }
        )
        return True if response.status_code < 300 else False

    def send_otp_to_one(self, recipient: str, otp: str) -> bool | ValidationError:
        """
        @recipients add a user number like 8801681845722.
        @message write message for the recipient users.
        Response will be true if sms response is 200.
        """
        return self.send_otp([recipient], otp)
