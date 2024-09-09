from django.db import models
from django.core.validators import BaseValidator
from functools import wraps
from typing import Any, Callable
from unittest import SkipTest
import inspect


# based on https://dev.to/anjalbam/testing-models-with-pytest-in-django-a-practical-approach-testing-django-applications-3410

def assert_attibute(attr_name: str):
    "Compares expected attribute value with field attribute value."
    def get_func(method: Callable):
        @wraps(method)
        def wrapper(self: 'ModelFieldTest', *args, **kwargs):
            # e.g. self.unique
            exp_attr_value = getattr(self, attr_name)
            # False is equal to None value for if statement
            # e.g. if False <=> if None
            if exp_attr_value is None:
                raise SkipTest('Empty field')

            # e.g. self.field.unique
            field_attr_value = getattr(self.field, attr_name)
            assert field_attr_value == exp_attr_value, \
                f'''Expected value {exp_attr_value} for field {attr_name} is not '''\
                f'''equal real value {field_attr_value}'''

        # for testing purposes
        setattr(wrapper, 'is_wrapped_by_assert_attibute', True)
        setattr(wrapper, 'attr_name', attr_name)
        return wrapper
    return get_func


class ModelFieldTest:
    '''
    Allows to test django model fields by subclasing this class and django test class.
    Every single class is dedicated to specified model field. Apart from basic
    field information like name and type for specified model, we can also test
    if it was created with specified attributes. Attributes are predefined.
    It is not possible to test `None` value for attribute.

    Example:
    ```
    from django.test import SimpleTestCase

    class NameFieldTest(ModelFieldTest, SimpleTestCase):
        model = User
        field_name = 'name'
        field_type = TextField

        default = ''
        primary_key = True

    ```
    '''
    model: type[models.Model]
    field_name: str
    field_type: type[models.Field]

    # ATTRIBUTES
    #
    # None means DO NOT TEST
    primary_key: bool | None = None
    default: Any | None = None
    verbose_name: str | None = None
    unique: bool | None = None
    max_length: int | None = None
    validators: list[BaseValidator] | None = None
    help_text: str | None = None
    null: bool | None = None
    blank: bool | None = None

    @property
    def field(self) -> models.Field:
        "Gets model class field object."
        return self.model._meta.get_field(self.field_name)

    def test_field_type(self):
        assert isinstance(self.field, self.field_type), \
            f"Field {self.field} has different type than {self.field_type}"

    @assert_attibute('primary_key')
    def test_primary_key(self): pass

    def test_default(self):
        if self.default is not None:
            # method/function assigned to value
            if any([
                inspect.ismethod(self.default),
                inspect.isfunction(self.default)
            ]):
                default_code = inspect.getsource(self.default)
                field_code = inspect.getsource(self.field.default)
                print(1, field_code)
                assert field_code == default_code, \
                    f'''Expected method {self.default.__name__} for field default is not '''\
                    f'''equal real method {self.field.default.__name__}'''
            # any other value
            else:
                assert self.field.default == self.default, \
                    f'''Expected value {self.default} for field default is not '''\
                    f'''equal real value {self.field.default}'''

    @assert_attibute('verbose_name')
    def test_verbose_name(self): pass

    @assert_attibute('unique')
    def test_unique(self): pass

    @assert_attibute('max_length')
    def test_max_length(self): pass

    def test_validators(self):
        if self.validators is not None:
            for validator in self.validators:
                assert validator in self.field.validators, \
                    'Validator not exists in validators list'

    @assert_attibute('help_text')
    def test_help_text(self): pass

    @assert_attibute('null')
    def test_null(self): pass

    @assert_attibute('blank')
    def test_blank(self): pass


#
#
#
#
#
#
#
#
#
#


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
        if self.value:
            assert self.field == self.value, \
                f'Expected value {self.value} not equal real value {self.field}'

    def test_value_type(self):
        if self.value_type:
            assert isinstance(self.field, self.value_type), \
                f'Expected type {self.value_type} for field {self.field_name} '\
                f'is not equal to real type {self.field.__class__}'

#
#
#
#
#
#
#
#
#
#


class MetaFieldTest(ClassFieldTest):
    '''
    Allows testing Meta nested class in django model. 
    Similar to `ClassFieldTest`.

    Example:
    ```
    class ConstraintsFieldTest(MetaFieldTest, SimpleTestCase):
        klass = User
        field_name = 'constraints'
        value = [
            models.UniqueConstraint(
                fields=['telephone_prefix', 'telephone_number'],
                name='telephone_number_with_prefix_unique'
            )
        ]
    ```
    '''
    @property
    def field(self) -> models.Field:
        "Gets nestred Meta class inside model class."
        return getattr(self.klass._meta, self.field_name)
