import pytest
from src import MetaFieldTest
from unittest.mock import MagicMock
from functools import partial
# getter


@pytest.fixture
def class_with_field():
    class T:
        attr = 1

    mock = MagicMock()
    mock.klass._meta = T
    mock.field_name = 'attr'

    return mock


@pytest.fixture
def class_without_field(class_with_field):
    class_with_field.field_name = 'another_field'
    return class_with_field


@pytest.fixture
def field_property_with_field(class_with_field):
    method = MetaFieldTest.field.fget
    method = partial(method, class_with_field)  # type: ignore
    return method


@pytest.fixture
def field_property_without_field(class_without_field):
    method = MetaFieldTest.field.fget
    method = partial(method, class_without_field)  # type: ignore
    return method


def test_field_exists(class_with_field, field_property_with_field):
    '''
    WHEN field exists
    THEN it gets field
    '''
    value = getattr(class_with_field.klass._meta, class_with_field.field_name)
    assert field_property_with_field() == value


def test_field_not_exists(field_property_without_field):
    '''
    WHEN field not exists
    THEN it raises exception
    '''
    with pytest.raises(AttributeError):
        field_property_without_field()
