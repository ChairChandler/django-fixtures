from typing import Optional
from django.db import models
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.core import validators
from django.core.mail import send_mail
from django.contrib.auth.models import BaseUserManager, AbstractUser
import uuid
from webapp.authapp.models import AppUser

# Create your models here.


class Telephone(models.Model):
    user = models.OneToOneField(
        AppUser,
        on_delete=models.CASCADE,
        primary_key=True
    )
    telephone_prefix = models.IntegerField(
        "telephone number prefix",
        default=48,
        # https://en.wikipedia.org/wiki/List_of_country_calling_codes
        validators=[
            validators.MinValueValidator(1, "Minimum value must be 1"),
            validators.MaxValueValidator(999, "Maximum value must be 999")
        ],
        help_text=''
    )
    telephone_number = models.CharField(
        "telephone number",
        max_length=9,
        validators=[
            validators.MinLengthValidator(9, "Invalid telephone value")
        ],
        help_text=''
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['telephone_prefix', 'telephone_number'],
                name='telephone_number_with_prefix_unique'
            )
        ]


class AppUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def with_perm(
        self, perm, is_active=True, include_superusers=True, backend=None, obj=None
    ):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)  # type: ignore
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


class AppUser(AbstractUser):
    email = models.EmailField(
        "email address",
        primary_key=True,
        max_length=64
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # remove fields from superclass
    username = None
    first_name = None
    last_name = None

    objects: AppUserManager = AppUserManager()  # type: ignore

    class InvalidEmail(ValueError):
        pass

    def get_full_name(self):
        return self.get_username()

    def get_short_name(self):
        return self.get_username()

    def email_user_with_status(self, subject, message, from_email=None, **kwargs) -> int:
        """Send an email to this user and return status code."""
        return send_mail(subject, message, from_email, [self.email], **kwargs)

    @staticmethod
    def create_admin(email: str, password: str):
        '''
        Create admin account.
        '''
        pwd_hashed = make_password(password)

        AppUser.objects.create_superuser(
            email=email,
            password=pwd_hashed
        )

    @staticmethod
    def create_user(email: str, telephone: Optional[Telephone] = None):
        '''
        Create hashed unique password and send email to the user with password.
        '''
        password = uuid.uuid4().hex
        pwd_hashed = make_password(password)

        user = AppUser.objects.create_user(
            email=email,
            password=pwd_hashed,
            telephone=telephone
        )
        is_email_sent = user.email_user_with_status(
            'Account created',
            f'Password: {password}',
            from_email='test@mail.com',
            fail_silently=False
        )
        if not is_email_sent:
            user.delete()
            msg = 'E-mail probably not exists - no password sent'
            raise AppUser.InvalidEmail(msg)
