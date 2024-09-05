from .base import *
from django.test import SimpleTestCase
from django.db import models
from django.core import validators
from accounts.models import User
from accounts.user_manager import UserManager
import uuid


# # Create your tests here.

class UuidFieldTest(ModelFieldTest, SimpleTestCase):
    model = User
    field_name = 'uuid'
    field_type = models.UUIDField

    default = uuid.uuid4
    primary_key = True


class EmailFieldTest(ModelFieldTest, SimpleTestCase):
    model = User
    field_name = 'email'
    field_type = models.EmailField

    verbose_name = 'email address'
    unique = True
    max_length = 64


class TelephonePrefixFieldTest(ModelFieldTest, SimpleTestCase):
    model = User
    field_name = 'telephone_prefix'
    field_type = models.IntegerField

    verbose_name = 'telephone number prefix'
    default = 48
    validators = [
        validators.MinValueValidator(1, "Minimum value must be 1"),
        validators.MaxValueValidator(999, "Maximum value must be 999")
    ]
    help_text = ''


class TelephoneNumberFieldTest(ModelFieldTest, SimpleTestCase):
    model = User
    field_name = 'telephone_number'
    field_type = models.CharField

    verbose_name = 'telephone number'
    max_length = 9
    null = True
    blank = True
    validators = [
        validators.MinLengthValidator(9, "Invalid telephone value")
    ]
    help_text = 'Required for user, optional for administrators'


# #
# #
# #
# #
# #
# #
# #
# #
# #
# #

class UppercasedUsernameFieldTest(ClassFieldTest, SimpleTestCase):
    klass = User
    field_name = 'USERNAME_FIELD'
    value = 'email'


class RequiredFieldsFieldTest(ClassFieldTest, SimpleTestCase):
    klass = User
    field_name = 'REQUIRED_FIELDS'
    value = []


class UsernameFieldTest(ClassFieldTest, SimpleTestCase):
    klass = User
    field_name = 'username'
    value = None


class FirstNameFieldTest(ClassFieldTest, SimpleTestCase):
    klass = User
    field_name = 'first_name'
    value = None


class LastNameFieldTest(ClassFieldTest, SimpleTestCase):
    klass = User
    field_name = 'last_name'
    value = None


class ObjectsFieldTest(ClassFieldTest, SimpleTestCase):
    klass = User
    field_name = 'objects'
    value_type = UserManager


# #
# #
# #
# #
# #
# #
# #
# #
# #
# #

class ConstraintsFieldTest(MetaFieldTest, SimpleTestCase):
    klass = User
    field_name = 'constraints'
    value = [
        models.UniqueConstraint(
            fields=['telephone_prefix', 'telephone_number'],
            name='telephone_number_with_prefix_unique'
        )
    ]
