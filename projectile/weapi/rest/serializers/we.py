from rest_framework import serializers

from accountio.models import Organization


class PrivateOrganizationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = (
            "uid",
            "name",
            "domain",
            "kind",
            "tax_number",
            "registration_no",
            "website_url",
            "blog_url",
            "linkedin_url",
            "instagram_url",
            "facebook_url",
            "twitter_url",
            "summary",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("uid", "created_at", "updated_at", "domain")
