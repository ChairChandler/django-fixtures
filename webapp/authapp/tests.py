from ast import Delete
import random
import string
from django.test import TestCase
from django.forms import ValidationError
from django.db import transaction  # type: ignore
from django.db.utils import IntegrityError
from unittest.mock import patch
from more_itertools import first

from .models import AppUser

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
        AppUser.objects.all().delete()

    # EMAIL FIELD

    def test_email_is_username(self):
        '''
        Email must be a username, being an user ID.
        '''
        # insert email
        example_mail = first(self.valid_emails)

        user = AppUser.objects.create(
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
            user = AppUser.objects.create(
                email=example_mail,
                telephone_number=self.telephones[0],
                password=self.passwords[0]
            )
            user.full_clean()
            self.assertEqual(user.email, example_mail)

        with transaction.atomic():
            # try insert it again
            with self.assertRaises(IntegrityError):
                AppUser.objects.create(
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
            user = AppUser.objects.create(
                email=email,
                telephone_number=first(self.telephones),
                password=first(self.passwords)
            )
            user.full_clean()
            # telephone must be unique - remove user
            user.delete()

        # insert invalid email format
        for email in self.invalid_emails:
            user = AppUser.objects.create(
                email=email,
                telephone_number=first(self.telephones),
                password=first(self.passwords)
            )
            with self.assertRaises(ValidationError):
                user.full_clean()

            # we cannot remove object like above, because fields are empty
            # so we have to find it in the database
            AppUser.objects.get(pk=email).delete()

        # insert invalid long emails
        long_mails = [
            ('valid', 'a'*50 + '@a.com'),
            ('valid', 'a'*58 + '@a.com'),
            ('invalid', 'a'*65 + '@a.com'),
            ('invalid', 'a@@a.com'),
        ]
        for mail_type, mail in long_mails:
            user = AppUser.objects.create(
                email=mail,
                telephone_number=first(self.telephones),
                password=first(self.passwords)
            )
            if mail_type == 'valid':
                user.full_clean()
            else:
                with self.assertRaises(ValidationError):
                    user.full_clean()

            AppUser.objects.get(pk=mail).delete()

    # TELEPHONE FIELD

    def test_phone_prefix_is_validated(self):
        '''
        Check if telephone prefix is in international range between 1 and 999.
        It shoud fail if prefix is out of range.
        '''
        for prefix in range(1, 999+1):
            with transaction.atomic():
                user = AppUser.objects.create(
                    email=first(self.valid_emails),
                    telephone_prefix=prefix,
                    telephone_number=first(self.telephones),
                    password=first(self.passwords)
                )
                user.full_clean()
                self.assertEqual(user.telephone_prefix, prefix)
                AppUser.objects.all().delete()

        for prefix in [0, 5000]:
            with transaction.atomic(), self.assertRaises(ValidationError):
                user = AppUser.objects.create(
                    email=first(self.valid_emails),
                    telephone_prefix=prefix,
                    telephone_number=first(self.telephones),
                    password=first(self.passwords)
                )
                # we have to run validators
                user.full_clean()
            AppUser.objects.all().delete()

    def test_phone_number_is_validated(self):
        '''
        Telephone number is a 9-length texts of digits.
        It should fail if length is different.
        '''
        # lets generate 100 positive samples
        for _ in range(100):
            with transaction.atomic():
                telephone_number = ''.join(random.choices(string.digits, k=9))
                user = AppUser.objects.create(
                    email=first(self.valid_emails),
                    telephone_number=telephone_number,
                    password=first(self.passwords)
                )
                user.full_clean()
                self.assertEqual(user.telephone_number, telephone_number)
            AppUser.objects.all().delete()

        # lets generate some negative samples
        invalid_range = [*range(1, 8+1), *range(10, 20+1)]
        for k in invalid_range:
            with transaction.atomic(), self.assertRaises(ValidationError):
                telephone_number = ''.join(random.choices(string.digits, k=k))
                user = AppUser.objects.create(
                    email=first(self.valid_emails),
                    telephone_number=telephone_number,
                    password=first(self.passwords)
                )
                user.full_clean()
            AppUser.objects.all().delete()

    def test_prefix_with_phone_number_are_unique(self):
        '''
        Telephone number combined with prefix must be unique.
        '''
        telephone_number = first(self.telephones)

        # insert first
        with transaction.atomic():
            user = AppUser.objects.create(
                email=self.valid_emails[0],
                telephone_number=telephone_number,
                password=self.passwords[0]
            )
            self.assertEqual(user.telephone_number, telephone_number)

        # insert second time
        with transaction.atomic(), self.assertRaises(IntegrityError):
            AppUser.objects.create(
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
            AppUser.objects.create(
                email=first(self.valid_emails),
                password=first(self.passwords)
            )
        AppUser.objects.all().delete()

        # also runs with telephone
        with transaction.atomic():
            telephone_number = first(self.telephones)
            user = AppUser.objects.create(
                email=first(self.valid_emails),
                telephone_number=telephone_number,
                password=first(self.passwords)
            )
            self.assertEqual(user.telephone_number, telephone_number)

    def test_telephone_can_be_deleted(self):
        '''
        Admin can remove telephone of the user.
        '''
        user: AppUser = AppUser.objects.create(
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
        AppUser.create_user(
            email=email,
            telephone_number=first(self.telephones)
        )
        self.assertTrue(AppUser.objects.get(pk=email))

    def test_create_admin_account(self):
        '''
        Admin account should be created using only email.
        '''
        email = first(self.valid_emails)
        AppUser.create_admin(email=email)
        self.assertTrue(AppUser.objects.get(pk=email))

    def test_email_sent_after_account_is_created(self):
        '''
        During account creation, random password is generated and sent to email.
        '''
        with patch('authapp.models.send_mail') as mock:
            # e-mail exists, so return 1
            mock.return_value = 1

            # check if email is sentfor normal account
            AppUser.create_user(
                email=self.valid_emails[0],
                telephone_number=first(self.telephones)
            )
            mock.assert_called()

            # check if email is sent for admin account
            AppUser.create_admin(email=self.valid_emails[1])
            mock.assert_called()

    def test_user_account_removed_for_invalid_email(self):
        '''
        If e-mail is invalid, then remove admin if we want to (by default).
        '''
        email = first(self.valid_emails)
        telephone_number = first(self.telephones)
        with patch('authapp.models.send_mail') as mock:
            # e-mail doesn't exists, so return 0
            mock.return_value = 0
            # email not exists, so user is not created
            with self.assertRaises(AppUser.InvalidEmail):
                AppUser.create_user(
                    email=email,
                    telephone_number=telephone_number,
                    delete_if_mail_not_exists=True
                )
            mock.assert_called()
            with self.assertRaises(AppUser.DoesNotExist):
                AppUser.objects.get(pk=email)

    def test_admin_account_removed_for_invalid_email(self):
        '''
        If e-mail is invalid, then remove user if we want to (by default).
        '''
        email = first(self.valid_emails)
        with patch('authapp.models.send_mail') as mock:
            # e-mail doesn't exists, so return 0
            mock.return_value = 0
            # email not exists, so admin is not created
            with self.assertRaises(AppUser.InvalidEmail):
                AppUser.create_admin(
                    email=email,
                    delete_if_mail_not_exists=True
                )
            mock.assert_called()
            with self.assertRaises(AppUser.DoesNotExist):
                AppUser.objects.get(pk=email)
