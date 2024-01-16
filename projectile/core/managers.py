from django.contrib import auth
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    def create_user(self, first_name, last_name, phone, password, **extra_fields):
        if not phone:
            raise ValidationError(_("Phone number is required"))
        if not password:
            raise ValidationError(_("Password is required"))
        extra_fields.setdefault("is_verified", True)

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.first_name = first_name.title()
        user.last_name = last_name.title()
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, phone, password, **extra_fields):
        extra_fields.setdefault("email", "")
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        user = self.create_user(first_name, last_name, phone, password, **extra_fields)
        return user

    def with_perm(
        self, perm, is_active=True, include_superusers=True, backend=None, obj=None
    ):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    "You have multiple authentication backends configured and "
                    "therefore must provide the `backend` argument."
                )
        elif not isinstance(backend, str):
            raise TypeError(
                "backend must be a dotted import path string (got %r)." % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, "with_perm"):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()
