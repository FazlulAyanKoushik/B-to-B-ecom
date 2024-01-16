import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from dirtyfields import DirtyFieldsMixin
from rest_framework.exceptions import ValidationError

User = get_user_model()


class UserPhoneOTP(DirtyFieldsMixin, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, unique=True)
    is_consumed = models.BooleanField(default=False)
    expired_at = models.DateTimeField()

    def __str__(self):
        return f"User: {self.user.phone}, Otp: {self.otp}"

    def is_expired(self):
        """Returns True if the OTP code has expired, False otherwise."""
        return self.expired_at < timezone.now()

    def save_if_status_is_consumed(self):
        self.is_consumed = True
        self.save_dirty_fields()

    def has_previous_request(self) -> bool:
        """
        Checks if the user has sent a request before the last data's expiration time.
        Returns True if a previous request exists, False otherwise.
        """
        expiration_window = datetime.timedelta(seconds=settings.OTP_EXPIRATION_TIME_SEC)
        expiration_start = timezone.now() + expiration_window
        previous_requests = UserPhoneOTP.objects.filter(
            user=self.user,
            expired_at__range=(timezone.now(), expiration_start),
            is_consumed=False,
        )
        return previous_requests.exists()

    def save(self, *args, **kwargs):
        if self.pk is None:
            if not self.expired_at:
                self.expired_at = timezone.now() + datetime.timedelta(
                    seconds=settings.OTP_EXPIRATION_TIME_SEC
                )
            if not self.otp:
                from otpio.utils.otp import OTP

                otp = OTP()
                self.otp = otp.generate_unique_otp()
            # if self.has_previous_request():
            #     raise ValidationError(
            #         {
            #             "detail": f"Please wait {settings.OTP_EXPIRATION_TIME_SEC} seconds after sending a request."
            #         }
            #     )

        super().save(*args, **kwargs)
