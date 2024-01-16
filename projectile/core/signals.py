from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.dispatch import receiver

from rest_framework.exceptions import ValidationError

User = get_user_model()


@receiver(pre_save, sender=User)
def add_order_unique_id(sender, instance, **kwargs):
    email = instance.email or ""
    if email:
        if instance.pk:
            if User.objects.filter(email=email).exclude(pk=instance.pk).exists():
                raise ValidationError(
                    {"email": "Email is already used by another user"}
                )
        else:
            if User.objects.filter(email=email).exists():
                raise ValidationError(
                    {"email": "Email is already used by another user"}
                )
