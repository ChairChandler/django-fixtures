class UserFixtures:
    @property
    def valid_emails(self):
        # https://codefool.tumblr.com/post/15288874550/list-of-valid-and-invalid-email-addresses
        return [
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

    @property
    def invalid_emails(self):
        return [
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

    @property
    def passwords(self):
        return [
            'pwd',
            'example'
        ]

    @property
    def telephones(self):
        return [
            '123456789',
            '000000000',
            '111111111',
            '444444444',
            '555555555'
        ]
