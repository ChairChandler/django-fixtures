from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.core import validators
import uuid

# Create your models here.


class Telephone(models.Model):
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
        max_length=64
    )
    telephone = models.OneToOneField(Telephone, on_delete=models.RESTRICT)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['telephone']

    # remove fields from superclass
    username = None
    first_name = None
    last_name = None

    class InvalidEmail(ValueError):
        pass

    # we cannot remove methods from base class, so we mark them
    def get_full_name(self):
        raise NotImplementedError('Method is forbidden')

    def get_short_name(self):
        raise NotImplementedError('Method is forbidden')

    @staticmethod
    def create_user(email: str, telephone: Telephone):
        '''
        Create hashed unique password and send email to the user with password.
        '''
        password = uuid.uuid4().hex
        pwd_hashed = make_password(password)

        user = AppUser.objects.create(
            email=email,
            telephone=telephone,
            password=pwd_hashed
        )
        is_email_sent = user.email_user(
            'Account created',
            f'Password: {password}',
            from_email='test@mail.com',
            fail_silently=False
        )
        if not is_email_sent:
            user.delete()
            msg = 'E-mail probably not exists - no password sent'
            raise AppUser.InvalidEmail(msg)
