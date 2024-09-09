import pytest
from src import ClassFieldTest
from unittest.mock import MagicMock
from functools import partial

#
#
# getter
#
#


@pytest.fixture
def class_with_field():
    class T:
        attr = 1

    mock = MagicMock()
    mock.klass = T
    mock.field_name = 'attr'

    return mock


@pytest.fixture
def class_without_field(class_with_field):
    class_with_field.field_name = 'another_field'
    return class_with_field


@pytest.fixture
def field_property_with_field(class_with_field):
    method = ClassFieldTest.field.fget
    method = partial(method, class_with_field)  # type: ignore
    return method


@pytest.fixture
def field_property_without_field(class_without_field):
    method = ClassFieldTest.field.fget
    method = partial(method, class_without_field)  # type: ignore
    return method


def test_field_exists(class_with_field, field_property_with_field):
    '''
    WHEN field exists
    THEN it gets field
    '''
    value = getattr(class_with_field.klass, class_with_field.field_name)
    assert field_property_with_field() == value


def test_field_not_exists(field_property_without_field):
    '''
    WHEN field not exists
    THEN it raises exception
    '''
    with pytest.raises(AttributeError):
        field_property_without_field()

#
#
# value
#
#


@pytest.fixture
def empty_value():
    return MagicMock(value=None)


@pytest.fixture
def empty_value_method(empty_value):
    return partial(ClassFieldTest.test_value, empty_value)


@pytest.fixture
def valid_value_method(empty_value):
    empty_value.value = 1
    empty_value.field = 1

    return partial(ClassFieldTest.test_value, empty_value)


@pytest.fixture
def invalid_value_method(empty_value):
    empty_value.value = 1
    empty_value.field = 2

    return partial(ClassFieldTest.test_value, empty_value)


def test_value_empty_value(empty_value_method):
    '''
    WHEN value is None
    THEN it pass
    '''
    empty_value_method()


def test_value_valid(valid_value_method):
    '''
    GIVEN value assigned to field
    WHEN field value is expected value
    THEN it pass
    '''
    valid_value_method()


def test_value_invalid(invalid_value_method):
    '''
    GIVEN value assigned to field
    WHEN field value is not expected value
    THEN it raises exception
    '''
    with pytest.raises(AssertionError):
        invalid_value_method()

#
#
# value_type
#
#


@pytest.fixture
def empty_value_type():
    return MagicMock(value_type=None)


@pytest.fixture
def empty_type_method(empty_value_type):
    return partial(ClassFieldTest.test_value_type, empty_value_type)


@pytest.fixture
def valid_type_method(empty_value_type):
    class T:
        pass
    empty_value_type.value_type = T
    empty_value_type.field = T()

    return partial(ClassFieldTest.test_value_type, empty_value_type)


@pytest.fixture
def invalid_type_method(empty_value_type):
    class X:
        pass

    class Y:
        pass
    empty_value_type.value_type = Y
    empty_value_type.field = X()

    return partial(ClassFieldTest.test_value_type, empty_value_type)


def test_value_type_empty_value(empty_type_method):
    '''
    WHEN value type is None
    THEN it pass
    '''
    empty_type_method()


def test_value_type_valid(valid_type_method):
    '''
    GIVEN object type assigned to field
    WHEN field object type is expected object type
    THEN it pass
    '''
    valid_type_method()


def test_value_type_invalid(invalid_type_method):
    '''
    GIVEN object type assigned to field
    WHEN field object type is not expected object type
    THEN it raises exception
    '''
    with pytest.raises(AssertionError):
        invalid_type_method()
