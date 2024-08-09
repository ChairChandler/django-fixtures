from unittest.mock import patch
from django.test import TestCase
from django.forms import ValidationError
from django.db import transaction  # type: ignore
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
import random
import string

from . import models

# Create your tests here.


class TelephoneModelTest(TestCase):
    def test_phone_prefix_in_range(self):
        '''
        Check if telephone prefix is in international range between 1 and 999.
        It shoud fail if prefix is out of range.
        '''
        example_tel_num = '000000000'
        for prefix in range(1, 999+1):
            o = models.Telephone.objects.create(
                telephone_prefix=prefix,
                telephone_number=example_tel_num
            )
            o.full_clean()
            self.assertEqual(o.telephone_prefix, prefix)

        for prefix in [0, 5000]:
            with self.assertRaises(ValidationError):
                o = models.Telephone.objects.create(
                    telephone_prefix=prefix,
                    telephone_number=example_tel_num
                )
                # we have to run validators
                o.full_clean()

    def test_phone_number(self):
        '''
        Telephone number is a 9-length texts of digits.
        It should fail if length is different.
        '''
        # lets generate 100 positive samples
        for _ in range(100):
            v = ''.join(random.choices(string.digits, k=9))
            o = models.Telephone.objects.create(telephone_number=v)
            o.full_clean()
            self.assertEqual(o.telephone_number, v)

        # lets generate some negative samples
        for k in [*range(1, 8+1), *range(10, 20+1)]:
            with self.assertRaises(ValidationError):
                v = ''.join(random.choices(string.digits, k=k))
                o = models.Telephone.objects.create(telephone_number=v)
                o.full_clean()

    def test_prefix_with_phone_number_are_unique(self):
        '''
        Telephone number combined with prefix must be unique.
        '''
        # lets generate sample
        v = ''.join(random.choices(string.digits, k=9))

        # insert first
        o = models.Telephone.objects.create(telephone_number=v)
        self.assertEqual(o.telephone_number, v)

        # insert second time
        with self.assertRaises(IntegrityError):
            models.Telephone.objects.create(telephone_number=v)


class AppUserModelTest(TestCase):
    User: models.AppUser = get_user_model()  # type: ignore

    def setUp(self) -> None:
        self.telephones = [
            models.Telephone.objects.create(telephone_number='123456789'),
            models.Telephone.objects.create(telephone_number='000000000')
        ]
        self.mails = [
            'example@mail.com',
            'another@mail.com'
        ]
        self.password = 'pwd'

        # https://codefool.tumblr.com/post/15288874550/list-of-valid-and-invalid-email-addresses
        self.valid_emails = [
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

        self.invalid_emails = [
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

    def tearDown(self) -> None:
        self.User.objects.all().delete()
        models.Telephone.objects.all().delete()

    def test_email_is_username(self):
        '''
        Email must be a username, being an user ID.
        '''
        # insert mail
        o = self.User.objects.create(
            email=self.mails[1],
            telephone=self.telephones[1],
            password=self.password
        )
        o.full_clean()
        self.assertEqual(o.email, self.mails[1])

        # check username
        self.assertEqual(o.get_username(), self.mails[1])

    def test_telephone_is_optional(self):
        '''
        Telephone number can be empty.
        '''
        # it runs without telephone
        with transaction.atomic():
            self.User.objects.create(
                email=self.mails[0],
                password=self.password
            )

        # also runs with telephone
        with transaction.atomic():
            o = self.User.objects.create(
                email=self.mails[1],
                password=self.password,
                telephone=self.telephones[0]
            )
            self.assertEqual(o.telephone, self.telephones[0])

    def test_telephone_can_be_deleted(self):
        '''
        Admin can remove telephone of the user.
        '''
        o = self.User.objects.create(
            email=self.mails[0],
            telephone=self.telephones[0],
            password=self.password
        )
        o.telephone.delete()  # type: ignore
        self.assertFalse(o.telephone.pk)  # type: ignore

    def test_email_is_unique(self):
        '''
        Email must be used once.
        '''
        with transaction.atomic():
            # insert mail
            o = self.User.objects.create(
                email=self.mails[0],
                telephone=self.telephones[0],
                password=self.password
            )
            o.full_clean()
            self.assertEqual(o.email, self.mails[0])

        with transaction.atomic():
            # try insert it again
            with self.assertRaises(IntegrityError):
                self.User.objects.create(
                    email=self.mails[0],
                    telephone=self.telephones[0],
                    password=self.password
                )

    def test_email_format(self):
        '''
        Email must followed international format as below:
        - username part: 64 chars
        - @ part: 1 char
        - domainame part: 255 chars
        '''
        # insert valid email format
        for email in self.valid_emails:
            o = self.User.objects.create(
                email=email,
                telephone=self.telephones[0],
                password=self.password
            )
            o.full_clean()
            # telephone must be unique - remove user
            o.delete()

        # insert invalid email format
        for email in self.invalid_emails:
            o = self.User.objects.create(
                email=email,
                telephone=self.telephones[0],
                password=self.password
            )
            with self.assertRaises(ValidationError):
                o.full_clean()

            # we cannot remove object like above, because fields are empty
            # so we have to find it in the database
            self.User.objects.get(pk=email).delete()

        # insert invalid long emails
        long_mails = [
            ('valid', 'a'*50 + '@a.com'),
            ('valid', 'a'*58 + '@a.com'),
            ('invalid', 'a'*65 + '@a.com'),
            ('invalid', 'a@@a.com'),
        ]
        for mail_type, mail in long_mails:
            o = self.User.objects.create(
                email=mail,
                telephone=self.telephones[0],
                password=self.password
            )
            if mail_type == 'valid':
                o.full_clean()
            else:
                with self.assertRaises(ValidationError):
                    o.full_clean()

            self.User.objects.get(pk=mail).delete()

    def test_admin_account_created(self):
        '''
        Admin account should be created using only email with prepared password.
        '''
        self.User.create_admin(self.mails[0], self.password)
        self.assertTrue(self.User.objects.get(pk=self.mails[0]))

    def test_random_password_generation_with_email_sent(self):
        '''
        During account creation, random password is generated and sent to the user email.
        '''
        # send_mail
        with patch('authapp.models.send_mail') as mock:
            mock.return_value = 1
            # email exists and password sent => user is created
            self.User.create_user(self.mails[0], self.telephones[0])
            mock.assert_called()
            self.assertTrue(self.User.objects.get(pk=self.mails[0]))

        with patch('authapp.models.send_mail') as mock:
            mock.return_value = 0
            # email not exists => user is not created
            with self.assertRaises(models.AppUser.InvalidEmail):
                self.User.create_user(self.mails[1], self.telephones[1])
            mock.assert_called()
            with self.assertRaises(self.User.DoesNotExist):
                self.User.objects.get(pk=self.mails[1])
