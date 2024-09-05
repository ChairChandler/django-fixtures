from email.policy import default
from django.test import SimpleTestCase
from django.db import models
from django.core.validators import BaseValidator
from typing import Any, Callable
from unittest import SkipTest
import inspect


# based on https://dev.to/anjalbam/testing-models-with-pytest-in-django-a-practical-approach-testing-django-applications-3410

__all__ = [
    'ModelFieldTest',
    'ClassFieldTest',
    'MetaFieldTest'
]


def assert_field(field_name: str):
    def get_func(method: Callable):
        def wrapper(self: 'ModelFieldTest', *args, **kwargs):
            value = getattr(self, field_name)
            # False is equal to None value for if statement
            # e.g. if False <=> if None
            if value is None:
                raise SkipTest('Empty field')

            field_value = getattr(self.field, field_name)
            assert field_value == value, \
                f'''Expected value {value} for field {field_name} is not '''\
                f'''equal real value {field_value}'''

        return wrapper
    return get_func


class ModelFieldTest:
    model: type[models.Model]
    field_name: str
    field_type: type[models.Field]

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
        return self.model._meta.get_field(self.field_name)

    def test_field_type(self):
        assert isinstance(self.field, self.field_type), \
            f"Field {self.field} has different type than {self.field_type}"

    @assert_field('primary_key')
    def test_primary_key(self): pass

    def test_default(self):
        if self.default is not None:
            if inspect.ismethod(self.default):
                default_code = inspect.getsource(self.default)
                field_code = inspect.getsource(self.field.default)
                assert field_code == default_code, \
                    f'''Expected method {self.default.__name__} for field default is not '''\
                    f'''equal real method {self.field.default.__name__}'''
            else:
                assert self.field.default == self.default, \
                    f'''Expected value {self.default} for field default is not '''\
                    f'''equal real value {self.field.default}'''

    @assert_field('verbose_name')
    def test_verbose_name(self): pass

    @assert_field('unique')
    def test_unique(self): pass

    @assert_field('max_length')
    def test_max_length(self): pass

    def test_validators(self):
        if self.validators is not None:
            for validator in self.validators:  # type: ignore
                assert validator in self.field.validators, \
                    'Validator not exists in validators list'

    @assert_field('help_text')
    def test_help_text(self): pass

    @assert_field('null')
    def test_null(self): pass

    @assert_field('blank')
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
    klass: type
    field_name: str
    value: Any | None = None
    value_type: type | None = None

    @property
    def field(self) -> models.Field:
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
    @property
    def field(self) -> models.Field:
        return getattr(self.klass._meta, self.field_name)
