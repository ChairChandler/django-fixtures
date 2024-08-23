from django.db import models
from django.core import validators
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractUser
import uuid

from .user_manager import UserManager

# Create your models here.


def validate_telephone(value: 'User'):
    "Telephone cannot not be empty for normal user."
    is_admin = (value.is_superuser or value.is_staff)
    if value.telephone_number is None and not is_admin:
        raise User.TelephoneError(
            'Telephone number cannot be empty for normal user'
        )


class User(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    email = models.EmailField(
        "email address",
        unique=True,
        max_length=64
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
        null=True,
        blank=True,
        validators=[
            validators.MinLengthValidator(9, "Invalid telephone value")
        ],
        help_text='Required for user, optional for administrators'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['telephone_prefix', 'telephone_number'],
                name='telephone_number_with_prefix_unique'
            )
        ]

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # remove fields from superclass
    username = None
    first_name = None
    last_name = None

    objects: UserManager = UserManager()  # type: ignore

    class TelephoneError(ValueError):
        pass

    def get_full_name(self):
        return self.get_username()

    def get_short_name(self):
        return self.get_username()

    def email_user_with_status(self, subject, message, from_email=None, **kwargs) -> int:
        """Send an email to this user and return status code."""
        return send_mail(subject, message, from_email, [self.email], **kwargs)

    def clean(self):
        super().clean()
        validate_telephone(self)
