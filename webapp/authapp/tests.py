import random
import string
from django.test import TestCase
from django.forms import ValidationError
from django.db import transaction  # type: ignore
from django.db.utils import IntegrityError
from unittest.mock import patch
from more_itertools import first

from .models import User

# Create your tests here.


class AppUserModelTest(TestCase):
    # https://codefool.tumblr.com/post/15288874550/list-of-valid-and-invalid-email-addresses
    valid_emails = [
        'email@example.com',
        'firstname.lastname@example.com',
        'email@subdomain.example.com',
        'firstname+lastname@example.com',
        'email@123.123.123.123',
        'email@[123.123.123.123]',
        '1234567890@example.com',
        'email@example-one.com',
        '_______@example.com',
        'email@example.name',
        'email@example.museum',
        'email@example.co.jp',
        'firstname-lastname@example.com',
        'email@example.web',
        'email@111.222.333.44444'
    ]

    invalid_emails = [
        'plainaddress',
        '# @%^%#$@#$@#.com',
        '@ example.com',
        'Joe Smith < email@example.com >',
        'email.example.com',
        'email@example@example.com',
        '.email@example.com',
        'email.@example.com',
        'email..email@example.com',
        'あいうえお@example.com',
        'email@example.com(Joe Smith)',
        'email@example',
        'email@-example.com',
        'email@example..com',
        'Abc..123@example.com',
        '“email”@ example.com'
    ]

    passwords = [
        'pwd',
        'example'
    ]

    telephones = [
        '123456789',
        '000000000'
    ]

    def tearDown(self):
        User.objects.all().delete()

    # EMAIL FIELD

    def test_email_is_username(self):
        '''
        Email must be a username, being an user ID.
        '''
        # insert email
        example_mail = first(self.valid_emails)

        user = User.objects.create(
            email=example_mail,
            password=first(self.passwords),
            telephone_number=first(self.telephones),
        )
        user.full_clean()

        # check email
        self.assertEqual(user.email, example_mail)

        # check username
        self.assertEqual(user.get_username(), example_mail)

    def test_email_is_unique(self):
        '''
        Email must be used once.
        '''
        example_mail = first(self.valid_emails)

        with transaction.atomic():
            # insert mail
            user = User.objects.create(
                email=example_mail,
                telephone_number=self.telephones[0],
                password=self.passwords[0]
            )
            user.full_clean()
            self.assertEqual(user.email, example_mail)

        with transaction.atomic():
            # try insert it again
            with self.assertRaises(IntegrityError):
                User.objects.create(
                    email=example_mail,
                    telephone_number=self.telephones[1],
                    password=self.passwords[1]
                )

    def test_email_is_validated(self):
        '''
        Email must pass email validator and the length must be less than 64 chars. 
        '''
        # insert valid email format
        for email in self.valid_emails:
            user = User.objects.create(
                email=email,
                telephone_number=first(self.telephones),
                password=first(self.passwords)
            )
            user.full_clean()
            # telephone must be unique - remove user
            user.delete()

        # insert invalid email format
        for email in self.invalid_emails:
            user = User.objects.create(
                email=email,
                telephone_number=first(self.telephones),
                password=first(self.passwords)
            )
            with self.assertRaises(ValidationError):
                user.full_clean()

            # we cannot remove object like above, because fields are empty
            # so we have to find it in the database
            User.objects.get(pk=email).delete()

        # insert invalid long emails
        long_mails = [
            ('valid', 'a'*50 + '@a.com'),
            ('valid', 'a'*58 + '@a.com'),
            ('invalid', 'a'*65 + '@a.com'),
            ('invalid', 'a@@a.com'),
        ]
        for mail_type, mail in long_mails:
            user = User.objects.create(
                email=mail,
                telephone_number=first(self.telephones),
                password=first(self.passwords)
            )
            if mail_type == 'valid':
                user.full_clean()
            else:
                with self.assertRaises(ValidationError):
                    user.full_clean()

            User.objects.get(pk=mail).delete()

    # TELEPHONE FIELD

    def test_phone_prefix_is_validated(self):
        '''
        Check if telephone prefix is in international range between 1 and 999.
        It shoud fail if prefix is out of range.
        '''
        for prefix in range(1, 999+1):
            with transaction.atomic():
                user = User.objects.create(
                    email=first(self.valid_emails),
                    telephone_prefix=prefix,
                    telephone_number=first(self.telephones),
                    password=first(self.passwords)
                )
                user.full_clean()
                self.assertEqual(user.telephone_prefix, prefix)
                User.objects.all().delete()

        for prefix in [0, 5000]:
            with transaction.atomic(), self.assertRaises(ValidationError):
                user = User.objects.create(
                    email=first(self.valid_emails),
                    telephone_prefix=prefix,
                    telephone_number=first(self.telephones),
                    password=first(self.passwords)
                )
                # we have to run validators
                user.full_clean()
            User.objects.all().delete()

    def test_phone_number_is_validated(self):
        '''
        Telephone number is a 9-length texts of digits.
        It should fail if length is different.
        '''
        # lets generate 100 positive samples
        for _ in range(100):
            with transaction.atomic():
                telephone_number = ''.join(random.choices(string.digits, k=9))
                user = User.objects.create(
                    email=first(self.valid_emails),
                    telephone_number=telephone_number,
                    password=first(self.passwords)
                )
                user.full_clean()
                self.assertEqual(user.telephone_number, telephone_number)
            User.objects.all().delete()

        # lets generate some negative samples
        invalid_range = [*range(1, 8+1), *range(10, 20+1)]
        for k in invalid_range:
            with transaction.atomic(), self.assertRaises(ValidationError):
                telephone_number = ''.join(random.choices(string.digits, k=k))
                user = User.objects.create(
                    email=first(self.valid_emails),
                    telephone_number=telephone_number,
                    password=first(self.passwords)
                )
                user.full_clean()
            User.objects.all().delete()

    def test_prefix_with_phone_number_are_unique(self):
        '''
        Telephone number combined with prefix must be unique.
        '''
        telephone_number = first(self.telephones)

        # insert first
        with transaction.atomic():
            user = User.objects.create(
                email=self.valid_emails[0],
                telephone_number=telephone_number,
                password=self.passwords[0]
            )
            self.assertEqual(user.telephone_number, telephone_number)

        # insert second time
        with transaction.atomic(), self.assertRaises(IntegrityError):
            User.objects.create(
                email=self.valid_emails[1],
                telephone_number=telephone_number,
                password=self.passwords[1]
            )

    def test_telephone_is_optional(self):
        '''
        Telephone number can be empty.
        '''
        # it runs without telephone
        with transaction.atomic():
            User.objects.create(
                email=first(self.valid_emails),
                password=first(self.passwords)
            )
        User.objects.all().delete()

        # also runs with telephone
        with transaction.atomic():
            telephone_number = first(self.telephones)
            user = User.objects.create(
                email=first(self.valid_emails),
                telephone_number=telephone_number,
                password=first(self.passwords)
            )
            self.assertEqual(user.telephone_number, telephone_number)

    def test_telephone_can_be_deleted(self):
        '''
        Admin can remove telephone of the user.
        '''
        user: User = User.objects.create(
            email=first(self.valid_emails),
            telephone_number=first(self.telephones),
            password=first(self.passwords)
        )
        user.telephone_number = None  # type: ignore
        user.save()
        self.assertFalse(user.telephone_number)

    # CREATE USER METHOD

    def test_create_user_account(self):
        '''
        User account should be created using email and telephone.
        '''
        email = first(self.valid_emails)
        User.objects.create_user(
            email=email,
            telephone_number=first(self.telephones)
        )
        self.assertTrue(User.objects.get(pk=email))

    def test_create_admin_account(self):
        '''
        Admin account should be created using only email.
        '''
        # test superuser
        email = self.valid_emails[0]
        User.objects.create_superuser(email=email, is_superuser=True)
        self.assertTrue(User.objects.get(pk=email))
        # test admin
        email = self.valid_emails[1]
        User.objects.create_user(email=email, is_staff=True)
        self.assertTrue(User.objects.get(pk=email))
