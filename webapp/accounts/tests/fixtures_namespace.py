from accounts.models import User


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


class MethodsFixtures:
    @property
    def get_full_name(self):
        return User.get_full_name

    @property
    def get_short_name(self):
        return User.get_short_name

    @property
    def email_user_with_status(self):
        return User.email_user_with_status

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
