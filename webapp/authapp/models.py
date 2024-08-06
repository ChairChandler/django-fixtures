from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core import validators
import uuid

# Create your models here.


class Telephone(models.Model):
    id = models.AutoField(primary_key=True, default=0)
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


class AppUser(AbstractUser):
    email = models.EmailField(
        "email address",
        primary_key=True,
        # https://www.lifewire.com/is-email-address-length-limited-1171110
        max_length=320
    )
    telephone = models.OneToOneField(Telephone, on_delete=models.RESTRICT)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['telephone']

    # remove fields from superclass
    username = None
    first_name = None
    last_name = None

    # we cannot remove methods from base class, so we mark them
    def get_full_name(self):
        raise NotImplementedError('Method is forbidden')

    def get_short_name(self):
        raise NotImplementedError('Method is forbidden')

    def create_password_and_send_email(self):
        random_data = uuid.uuid4().hex
        pwd = self.set_password(random_data)
        self.email_user(
            'Account created',
            f'Password: {pwd}',
            from_email=''
        )
