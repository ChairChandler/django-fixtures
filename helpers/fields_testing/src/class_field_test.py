from django.db import models
from typing import Any


class ClassFieldTest:
    '''
    Allows to test any class fields by subclasing this and django testing class.
    It's similar to `ModelFieldTest`, however more generic and limited for 
    testing specified field with value and value type.

    Example
    ```
    from django.test import SimpleTestCase

    class UppercasedUsernameFieldTest(ClassFieldTest, SimpleTestCase):
        klass = User
        field_name = 'USERNAME_FIELD'
        value = 'email'
    ```
    '''
    klass: type
    field_name: str
    value: Any | None = None
    value_type: type | None = None

    @property
    def field(self) -> models.Field:
        "Gets normal class field value."
        return getattr(self.klass, self.field_name)

    def test_value(self):
        if self.value is not None:
            assert self.field == self.value, \
                f'Expected value {self.value} not equal real value {self.field}'

    def test_value_type(self):
        if self.value_type is not None:
            assert isinstance(self.field, self.value_type), \
                f'Expected type {self.value_type} for field {self.field_name} '\
                f'is not equal to real type {self.field.__class__}'
