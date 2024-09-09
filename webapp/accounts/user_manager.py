from django.contrib.auth.models import (
    BaseUserManager,
    UserManager as OldUserManager
)
import uuid

import accounts.models as models


class UserManager(BaseUserManager):
    # Same as in OldUserManager
    use_in_migrations = True

    @staticmethod
    def _generate_password():
        return uuid.uuid4().hex

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.

        Raises:
            ValidationError
        """
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        user: models.User = self.model(email=email, **extra_fields)

        if password is None:
            password = self._generate_password()

        user.set_password(password)
        # check the model
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        # Method similar to OldUserManager.create_user.
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        # Method similar to OldUserManager.create_superuser.
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    # Same method as in OldUserManager
    with_perm = OldUserManager.with_perm
