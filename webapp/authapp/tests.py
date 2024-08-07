from django.test import TestCase

# Create your tests here.


class TelephoneModelTest(TestCase):
    def test_auto_generated_ids(self):
        pass

    def test_phone_prefix_in_range(self):
        pass

    def test_phone_number(self):
        pass

    def test_prefix_with_phone_number_are_unique(self):
        pass


class AppUserModelTest(TestCase):
    def test_email_is_username(self):
        pass

    def test_telephone_is_required(self):
        pass

    def test_email_is_unique(self):
        pass

    def test_email_format(self):
        # username part: 64 chars
        # @ part: 1 char
        # domainame part: 255 chars
        pass

    def test_telephone_cannot_be_deleted(self):
        # cannot be deleted
        pass

    def test_random_password_generation_with_email_sent(self):
        pass
