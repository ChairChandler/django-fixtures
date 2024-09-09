from typing import Generator
from django.test import SimpleTestCase
from accounts.tests.fixtures_namespace import MethodsFixtures
import fixture


@fixture.use_fixture_namespace(MethodsFixtures)
class GetFullNameMethodTest(SimpleTestCase):
    def test_gets_username_field(
        self,
        get_full_name: Generator[dict, None, None]
    ):
        'Method calls get_username method to get USERNAME_FIELD value.'
        meta = next(get_full_name)
        self.assertEqual(meta['method'](), meta['email'])


@fixture.use_fixture_namespace(MethodsFixtures)
class GetShortNameMethodTest(SimpleTestCase):
    def test_gets_username_field(
            self,
            get_short_name: Generator[dict, None, None]
    ):
        'Method calls get_username method to get USERNAME_FIELD value.'
        meta = next(get_short_name)
        self.assertEqual(meta['method'](), meta['email'])


@fixture.use_fixture_namespace(MethodsFixtures)
class EmailUserWithStatusMethodTest(SimpleTestCase):
    def test_call_send_mail(
            self,
            email_user_with_status: Generator[dict, None, None],
            subject: str,
            message: str,
            from_email: str,
            kwargs_headers: dict
    ):
        'Method calls send_mail method to send email.'
        meta = next(email_user_with_status)
        status = meta['method'](
            subject,
            message,
            from_email,
            **kwargs_headers
        )
        self.assertTrue(status)
        meta['send_mail'].assert_called_once_with(
            subject,
            message,
            from_email,
            [meta['email']],
            **kwargs_headers
        )
