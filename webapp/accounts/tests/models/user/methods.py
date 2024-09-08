from typing import Callable
from django.test import SimpleTestCase
from unittest.mock import patch
from accounts.models import User
from accounts.tests.fixtures_namespace import MethodsFixtures
import fixture


@fixture.use_fixture_namespace(MethodsFixtures)
class GetFullNameMethodTest(SimpleTestCase):
    MethodAnnotation = Callable[[User], str]

    def test_gets_username_field(
            self,
            get_full_name: MethodAnnotation,
            email: str
    ):
        'Method calls get_username method to get USERNAME_FIELD value.'
        with patch('accounts.models.User') as UserMock:
            user = UserMock()
            user.get_username.return_value = email

            self.assertEqual(get_full_name(user), email)


@fixture.use_fixture_namespace(MethodsFixtures)
class GetShortNameMethodTest(SimpleTestCase):
    MethodAnnotation = Callable[[User], str]

    def test_gets_username_field(
            self,
            get_short_name: MethodAnnotation,
            email: str
    ):
        'Method calls get_username method to get USERNAME_FIELD value.'
        with patch('accounts.models.User') as UserMock:
            user = UserMock()
            user.get_username.return_value = email

            self.assertEqual(get_short_name(user), email)


@fixture.use_fixture_namespace(MethodsFixtures)
class EmailUserWithStatusMethodTest(SimpleTestCase):
    MethodAnnotation = Callable[[User, str, str, str | None], int]

    def test_call_send_mail(
            self,
            email_user_with_status: MethodAnnotation,
            email: str,
            subject: str,
            message: str,
            from_email: str,
            kwargs_headers: dict
    ):
        'Method calls send_mail method to send email.'
        with (
            patch('accounts.models.send_mail') as send_mail_mock,
            patch('accounts.models.User') as UserMock,
        ):
            user = UserMock()
            user.email = email
            send_mail_mock.return_value = True

            status = User.email_user_with_status(
                user,
                subject,
                message,
                from_email,
                **kwargs_headers
            )
            self.assertTrue(status)
            send_mail_mock.assert_called_once_with(
                subject,
                message,
                from_email,
                [email],
                **kwargs_headers
            )
