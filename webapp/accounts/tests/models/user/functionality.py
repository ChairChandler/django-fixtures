from django.test import TestCase
from django.core import mail
from accounts.models import User
from accounts.tests.fixtures_namespace import ModelFixtures
from unittest.mock import patch
import fixture

# Create your tests here.


@fixture.use_fixture_namespace(ModelFixtures)
class CreateUserTest(TestCase):
    def tearDown(self):
        User.objects.all().delete()

    '''
    TITLE: User account creation
    
    AS a site owner
    I WANT user account to be created using email and telephone
    SO THAT I can send send him email or make a call
    '''

    def test_create_user_account(
        self,
        email: str,
        telephone: str
    ):
        '''
        SCENARIO 1: User account must be created using email and telephone
        WHEN user account is created using email and telephone
        THEN it's saved in database
        '''
        u = User.objects.create_user(
            email=email,
            telephone_number=telephone
        )
        self.assertTrue(User.objects.get(email=email))

    def test_telephone_is_required_for_user(
        self,
        email: str,
        password: str
    ):
        '''
        SCENARIO 2: User account without telephone must not be created
        WHEN creating user account without telephone
        THEN it raise exception
        '''
        with self.assertRaises(User.TelephoneError):
            User.objects.create(
                email=email,
                password=password
            )

    '''
    TITLE: User account modification
    
    AS a site owner
    I WANT user telephone number to be deleted after account creation
    SO THAT I can protect personal data
    '''

    def test_telephone_can_be_later_deleted(self, user: User):
        '''
        SCENARIO: User telephone number can be removed

        GIVEN user account is created
        WHEN telephone is deleted and changed in database
        THEN it pass
        '''
        user.telephone_number = None
        user.full_clean()
        user.save()

    '''
    TITLE: Send email with password to user
    
    AS a site owner
    I WANT automatically send email with password to user aftert account creation
    SO THAT user can sign in
    '''

    def test_valid_email_send(
        self,
        email: str,
        telephone: str
    ):
        '''
        SCENARIO 1: Send email with password to valid email

        GIVEN email exists
        WHEN user account is created
        THEN send email with password
        '''
        User.objects.create_user(
            email=email,
            telephone_number=telephone
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], email)
        self.assertEqual(mail.outbox[0].subject, 'Account created')
        self.assertIn('password', mail.outbox[0].body.lower())

    def test_invalid_email_send(
        self,
        email: str,
        telephone: str
    ):
        '''
        SCENARIO 2: Send email with password to invalid email

        GIVEN email not exists
        WHEN user account is created
        THEN it raise exception
        '''
        with patch('accounts.models.User.email_user_with_status') as mock:
            mock.return_value = False
            with self.assertRaises(User.EmailError):
                User.objects.create_user(
                    email=email,
                    telephone_number=telephone
                )
            mock.assert_called_once()


@fixture.use_fixture_namespace(ModelFixtures)
class CreateAdminTest(TestCase):
    def tearDown(self):
        User.objects.all().delete()

    '''
    TITLE: Admins account creation
    
    AS a site owner
    I WANT admin or superuser account to be created using email and optional telephone
    SO THAT I don't have to call to them if they don't want to
    '''

    def test_create_admin_account(self, email: str):
        '''
        SCENARIO 1: Admin account must be created using only email
        WHEN admin account is created using email
        THEN it's saved in database
        '''
        User.objects.create_user(email=email, is_staff=True)
        self.assertTrue(User.objects.get(email=email))

    def test_create_superuser_account(self, email: str):
        '''
        SCENARIO 2: Superuser account must be created using only email
        WHEN superuser account is created using email
        THEN it's saved in database
        '''
        User.objects.create_superuser(email=email)
        self.assertTrue(User.objects.get(email=email))

    def test_telephone_is_optional_for_admin(
        self,
        email: str,
        telephone: str
    ):
        '''
        SCENARIO 3: Telephone number can be empty for admin during account creation
        WHEN admin account is created using email with telephone number
        THEN it's saved in database
        '''
        User.objects.create_user(
            email=email,
            telephone_number=telephone,
            is_staff=True
        )
        self.assertTrue(User.objects.get(telephone_number=telephone))

    def test_telephone_is_optional_for_superuser(
        self,
        email: str,
        telephone: str
    ):
        '''
        SCENARIO 4: Telephone number can be empty for superuser during account 
        creation
        WHEN superuser account is created using email with telephone number
        THEN it's saved in database
        '''
        User.objects.create_user(
            email=email,
            telephone_number=telephone,
            is_superuser=True
        )
        self.assertTrue(User.objects.get(telephone_number=telephone))

    '''
    TITLE: Send email with password to admin
    
    AS a site owner
    I WANT send email with password to admin
    SO THAT admin can sign in
    '''

    def test_valid_admin_email_send(self, email: str,):
        '''
        SCENARIO 1: Send email with password to valid admin email

        GIVEN admin email exists
        WHEN admin account is created
        THEN send email with password
        '''
        User.objects.create_user(
            email=email,
            is_staff=True
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], email)
        self.assertEqual(mail.outbox[0].subject, 'Account created')
        self.assertIn('password', mail.outbox[0].body.lower())

    def test_valid_superuser_email_send(self, email: str):
        '''
        SCENARIO 2: Send email with password to valid superuser email

        GIVEN superuser email exists
        WHEN superuser account is created
        THEN send email with password
        '''
        User.objects.create_superuser(email=email)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], email)
        self.assertEqual(mail.outbox[0].subject, 'Account created')
        self.assertIn('password', mail.outbox[0].body.lower())

    def test_invalid_admin_email_send(self, email: str):
        '''
        SCENARIO 3: Send email with password to invalid admin email

        GIVEN email not exists
        WHEN admin account is created
        THEN it raise exception
        '''
        with patch('accounts.models.User.email_user_with_status') as mock:
            mock.return_value = False
            with self.assertRaises(User.EmailError):
                User.objects.create_user(email=email, is_staff=True)
            mock.assert_called_once()

    def test_invalid_superuser_email_send(self, email: str):
        '''
        SCENARIO 4: Send email with password to invalid superuser email

        GIVEN email not exists
        WHEN superuser account is created
        THEN it raise exception
        '''
        with patch('accounts.models.User.email_user_with_status') as mock:
            mock.return_value = False
            with self.assertRaises(User.EmailError):
                User.objects.create_superuser(email=email)
            mock.assert_called_once()
