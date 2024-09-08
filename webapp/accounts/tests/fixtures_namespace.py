from accounts.models import User
from unittest.mock import patch
from functools import partial


class ModelFixtures:
    @property
    def email(self):
        return 'email@example.com'

    @property
    def password(self):
        return 'example_password'

    @property
    def telephone(self):
        return '123456789'

    @property
    def user(self):
        return User.objects.create_user(
            email=self.email,
            password=self.password,
            telephone_number=self.telephone
        )
        
    @property
    def send_mail_mock(self):
        with patch('accounts.models.User.email_user_with_status') as mock:
            mock.return_value = False
            yield mock


class MethodsFixtures:
    @property
    def get_full_name(self):
        with patch('accounts.models.User') as UserMock:
            user = UserMock()
            user.get_username.return_value = self.email
            
            yield {
                'method': partial(User.get_full_name, user), 
                'email': self.email
            }

    @property
    def get_short_name(self):
        with patch('accounts.models.User') as UserMock:
            user = UserMock()
            user.get_username.return_value = self.email

            yield {
                'method': partial(User.get_short_name, user),
                'email': self.email
            }

    @property
    def email_user_with_status(self):
        with (
                patch('accounts.models.send_mail') as send_mail_mock,
                patch('accounts.models.User') as UserMock,
        ):
            user = UserMock()
            user.email = self.email
            send_mail_mock.return_value = True
            
            yield {
                'method': partial(User.email_user_with_status, user),
                'send_mail': send_mail_mock,
                'email': self.email
            }

    @property
    def email(self):
        return 'example@mail.com'

    @property
    def subject(self):
        return 'Example subject'

    @property
    def message(self):
        return 'Example message'

    @property
    def from_email(self):
        return 'from@mail.com'

    @property
    def kwargs_headers(self):
        return {'custom_header': 'value'}
