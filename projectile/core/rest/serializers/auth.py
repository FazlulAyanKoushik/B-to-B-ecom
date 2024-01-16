from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import (
    IntegrityError,
    transaction,
)

from phonenumber_field.serializerfields import PhoneNumberField

from rest_framework import (
    serializers,
    status,
)
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.response import Response

from accountio.choices import OrganizationUserRole
from accountio.models import (
    Organization,
    OrganizationUser,
)
from accountio.utils import get_subdomain

from core.utils import create_token

User = get_user_model()


class GlobalRefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=255)


class GlobalUserRegistrationSerializer(serializers.Serializer):
    slug = serializers.SlugField(read_only=True)
    first_name = serializers.CharField(label="Your first name", allow_blank=True)
    last_name = serializers.CharField(label="Your last name", allow_blank=True)
    phone = PhoneNumberField()
    password = serializers.CharField(min_length=6, write_only=True)
    email = serializers.EmailField(allow_blank=True)

    def validate_phone(self, value):
        organization = get_subdomain(self.context["request"])
        if OrganizationUser.objects.filter(
            user__phone=value, organization=organization
        ).exists():
            raise ValidationError("This phone number is already registered", code=422)
        return value

    def create(self, validated_data):
        with transaction.atomic():
            user, _ = User.objects.get_or_create(
                phone=validated_data.get("phone"),
                defaults={
                    "first_name": validated_data.get("first_name"),
                    "last_name": validated_data.get("last_name"),
                    "email": validated_data.get("email", ""),
                    "password": make_password(validated_data.get("password")),
                },
            )

            organization = get_subdomain(self.context["request"])
            try:
                OrganizationUser.objects.create(
                    organization=organization,
                    user=user,
                    role=OrganizationUserRole.CUSTOMER,
                    is_default=False,
                )
            except IntegrityError as e:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=e)

            validated_data["slug"] = user.slug
        return validated_data


class GlobalUserSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "uid",
            "first_name",
            "last_name",
            "phone",
        )
        read_only_fields = ("__all__",)


class GlobalOrganizationRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100, allow_blank=True)
    last_name = serializers.CharField(max_length=100, allow_blank=True)
    phone = PhoneNumberField()
    organization_name = serializers.CharField(max_length=255)
    organization_domain = serializers.CharField(
        max_length=255,
        allow_blank=True,
        required=False,
        help_text="If this field is null, it will automatically take the organization slug as its domain.",
    )
    password = serializers.CharField(max_length=255, write_only=True)
    retype_password = serializers.CharField(max_length=255, write_only=True)

    def validate_phone(self, data):
        try:
            User.objects.get(phone=data)
            raise ValidationError("Phone number is used by another user.")
        except User.DoesNotExist:
            return data

    def validate_organization_domain(self, data=""):
        try:
            Organization.objects.get(domain="-".join(data.lower().split(" ")))
            raise ValidationError(
                "This domain is used by another user. Please use another domain"
            )
        except Organization.DoesNotExist:
            if data:
                return "-".join(data.lower().split(" "))
            else:
                return ""

    def validate(self, attrs):
        first_name = attrs.get("first_name", "")
        last_name = attrs.get("last_name", "")
        password = attrs.get("password")
        retype_password = attrs.get("retype_password")
        if password != retype_password:
            raise ValidationError(
                {"retype_password": "Password is not match to re-type password"}
            )
        if first_name == "" and last_name == "":
            raise ValidationError("Please provide either first name or last name.")
        return attrs

    def create(self, validated_data):
        first_name = validated_data.get("first_name")
        last_name = validated_data.get("last_name")
        phone = validated_data.get("phone")
        organization_name = validated_data.get("organization_name")
        organization_domain = validated_data.get("organization_domain", "")
        password = validated_data.get("password")
        with transaction.atomic():
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                password=password,
            )

            organization = Organization.objects.create(
                name=organization_name, domain=organization_domain
            )
            OrganizationUser.objects.create(
                organization=organization,
                user=user,
                role=OrganizationUserRole.OWNER,
                is_default=True,
            )
            validated_data["organization_domain"] = organization.domain
            return validated_data


class UserLoginSerializer(serializers.Serializer):
    phone = serializers.SlugRelatedField(
        queryset=User.objects.filter(),
        slug_field="phone",
        write_only=True,
        error_messages={
            "does_not_exist": "Phone number does not exist.",
        },
    )
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(max_length=255, read_only=True)
    refresh = serializers.CharField(max_length=255, read_only=True)

    def validate(self, attrs):
        user = attrs.get("phone")
        password = attrs.get("password")

        if not user.check_password(password):
            raise AuthenticationFailed()

        return attrs

    def create(self, validated_data):
        user = validated_data.get("phone")
        validated_data["refresh"], validated_data["access"] = create_token(user)
        return validated_data
