from django.urls import reverse


def organization_domain_url(domain_name):
    return reverse("domain-availability-check", args=[domain_name])
