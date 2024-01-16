from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from accountio.models import OrganizationUser, Organization


@receiver(pre_save, sender=OrganizationUser)
def organizationuser_update_all_isdefault_organization(
    sender, instance, *args, **kwargs
):
    if instance.is_default:
        OrganizationUser.objects.filter(user=instance.user, is_default=True).update(
            is_default=False
        )


@receiver(post_save, sender=Organization)
def organization_set_domain_if_not_available(
    sender, instance, created, *args, **kwargs
):
    if not instance.domain:
        instance.domain = instance.slug
        instance.save()


@receiver(pre_save, sender=OrganizationUser)
def organizationuser_update_all_isdefault_organization(
    sender, instance, *args, **kwargs
):
    if instance.is_default:
        OrganizationUser.objects.filter(user=instance.user, is_default=True).update(
            is_default=False
        )
