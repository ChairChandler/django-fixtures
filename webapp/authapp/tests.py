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
    User = get_user_model()

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
            '“email”@ example.com',
            '1234567890@example.com',
            'email@example-one.com',
            '_______@example.com',
            'email@example.name',
            'email@example.museum',
            'email@example.co.jp',
            'firstname-lastname@example.com'
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
            'email@example.web',
            'email@111.222.333.44444',
            'email@example..com',
            'Abc..123@example.com'
        ]

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

    def test_telephone_is_required(self):
        '''
        Telephone number must be entered during creation.
        '''
        # it fails without telephone
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                self.User.objects.create(
                    email=self.mails[0],
                    password=self.password
                )

        # after fixing account is created
        with transaction.atomic():
            o = self.User.objects.create(
                email=self.mails[0],
                password=self.password,
                telephone=self.telephones[0]
            )
            self.assertEqual(o.telephone, self.telephones[0])  # type: ignore

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
        pass
        # insert valid email format
        # insert invalid email format
        # insert invalid email with username part more than 64 chars
        # insert invalid email with doubled @ char
        # insert invalid email with domain name part more than 255 chars

    def test_telephone_cannot_be_deleted(self):
        '''
        Admin or user can't remove telephone number.
        '''
        pass
        # admin tries to remove telephone number
        # user tries to remove telephone number

    def test_random_password_generation_with_email_sent(self):
        '''
        During account creation, random password is generated and sent to the user email.
        '''
        pass
        # email exists
        # email not exists
