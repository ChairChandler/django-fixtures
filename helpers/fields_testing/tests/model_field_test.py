from functools import partial
import pytest
from src import assert_attibute, ModelFieldTest
from unittest import SkipTest
from unittest.mock import MagicMock
import inspect


#
#
# assert_attibute decorator
#
#


@pytest.fixture
def not_existing_attribute():
    class T:
        @assert_attibute('attr')
        def test_attr(self): pass

    return T()


@pytest.fixture
def empty_attribute(not_existing_attribute):
    setattr(not_existing_attribute, 'attr', None)
    return not_existing_attribute


@pytest.fixture
def valid_field(not_existing_attribute):
    # in these situation we will not use self object
    def field(): return MagicMock(attr=1)
    field_property = property(field).fget()  # type: ignore

    setattr(not_existing_attribute, 'attr', 1)
    setattr(not_existing_attribute, 'field', field_property)

    return not_existing_attribute


@ pytest.fixture
def invalid_field(valid_field):
    setattr(valid_field, 'attr', 2)
    return valid_field


def test_assert_attibute_not_exists(not_existing_attribute):
    '''
    WHEN attribute not exists in class
    THEN raise exception
    '''
    with pytest.raises(AttributeError):
        not_existing_attribute.test_attr()


def test_assert_attibute_empty_value(empty_attribute):
    '''
    WHEN attribute in class has empty value
    THEN skip test
    '''
    with pytest.raises(SkipTest):
        empty_attribute.test_attr()


def test_assert_attibute_valid_field(valid_field):
    '''
    WHEN model field attribute equals expected attribute
    THEN it pass
    '''
    valid_field.test_attr()


def test_assert_attibute_invalid_field(invalid_field):
    '''
    WHEN model field attribute not equals expected attribute
    THEN it raise exception
    '''
    with pytest.raises(AssertionError):
        invalid_field.test_attr()

#
#
# getter
#
#


@ pytest.fixture
def model_with_field_name():
    field = MagicMock()

    mock = MagicMock()
    mock.field_name = 'field'
    mock.model._meta.get_field.return_value = field

    return {'self': mock, 'field': field}


@ pytest.fixture
def field_property(model_with_field_name):
    method = ModelFieldTest.field.fget
    method = partial(method, model_with_field_name['self'])  # type: ignore
    return method


def test_field(model_with_field_name, field_property):
    '''
    WHEN field exists
    THEN it gets field
    '''
    assert field_property() == model_with_field_name['field']

#
#
# all simple attributes
#
#


@ pytest.fixture
def attributes_wrapped_by_assert_attibute():
    # gets all methods
    methods = inspect.getmembers(ModelFieldTest, inspect.isfunction)
    # filter only to decorated by assert_attibute
    supported_attributes = [
        getattr(func, 'attr_name')
        for (_, func) in methods
        if hasattr(func, 'is_wrapped_by_assert_attibute')
    ]
    # remove duplicates
    return set(supported_attributes)


@pytest.fixture
def expected_attributes_wrapped_by_assert_attibute():
    return {
        'primary_key',
        'verbose_name',
        'unique',
        'max_length',
        'help_text',
        'null',
        'blank'
    }


def test_standard_attributes(
        attributes_wrapped_by_assert_attibute,
        expected_attributes_wrapped_by_assert_attibute
):
    '''
    GIVEN attribute list
    WHEN attributes are wrapped by assert_attibute
    THEN every attribute from list has test method wrapped by assert_attibute
    '''
    assert attributes_wrapped_by_assert_attibute == \
        expected_attributes_wrapped_by_assert_attibute

#
#
# field_type
#
#


@pytest.fixture
def valid_field_type():
    mock = MagicMock()
    mock.field = MagicMock()
    mock.field_type = MagicMock

    return mock


@pytest.fixture
def valid_field_type_method(valid_field_type):
    return partial(ModelFieldTest.test_field_type, valid_field_type)


@pytest.fixture
def invalid_field_type(valid_field_type):
    valid_field_type.field = 3
    valid_field_type.field_type = str

    return valid_field_type


@pytest.fixture
def invalid_field_type_method(invalid_field_type):
    return partial(ModelFieldTest.test_field_type, invalid_field_type)


def test_field_type_valid(valid_field_type_method):
    '''
    WHEN field is instance of expected field type
    THEN it pass
    '''
    valid_field_type_method()


def test_field_type_invalid(invalid_field_type_method):
    '''
    WHEN field is not instance of expected field type
    THEN it raise exception
    '''
    with pytest.raises(AssertionError):
        invalid_field_type_method()

#
#
# default
#
#


@pytest.fixture
def prepared_test_default_method():
    mock = MagicMock()
    method = partial(ModelFieldTest.test_default, mock)
    return {'method': method, 'mock': mock}


@pytest.fixture
def empty_test_default_method(prepared_test_default_method):
    prepared_test_default_method['mock'].default = None
    return prepared_test_default_method


@pytest.fixture
def valid_function_test_default_method(prepared_test_default_method):
    def fun(): pass
    prepared_test_default_method['mock'].default = fun
    prepared_test_default_method['mock'].field.default = fun
    return prepared_test_default_method


@pytest.fixture
def valid_method_test_default_method(prepared_test_default_method):
    class T:
        def meth(self): pass
    prepared_test_default_method['mock'].default = T().meth
    prepared_test_default_method['mock'].field.default = T().meth
    return prepared_test_default_method


@pytest.fixture
def invalid_function_test_default_method(prepared_test_default_method):
    def fun(): pass
    def nuf(): pass
    prepared_test_default_method['mock'].default = fun
    prepared_test_default_method['mock'].field.default = nuf
    return prepared_test_default_method


@pytest.fixture
def invalid_method_test_default_method(prepared_test_default_method):
    class T:
        def meth(self): pass

        def htem(self): pass
    prepared_test_default_method['mock'].default = T().meth
    prepared_test_default_method['mock'].field.default = T().htem
    return prepared_test_default_method


@pytest.fixture
def valid_other_test_default_method(prepared_test_default_method):
    prepared_test_default_method['mock'].default = 1
    prepared_test_default_method['mock'].field.default = 1
    return prepared_test_default_method


@pytest.fixture
def invalid_other_test_default_method(prepared_test_default_method):
    prepared_test_default_method['mock'].default = 1
    prepared_test_default_method['mock'].field.default = 4
    return prepared_test_default_method


def test_default_empty_value(empty_test_default_method):
    '''
    WHEN default is None
    THEN it pass
    '''
    empty_test_default_method['method']()


def test_default_valid_function_value(
        valid_function_test_default_method,
        valid_method_test_default_method,
):
    '''
    GIVEN method assigned to default field
    WHEN default is expected method
    THEN it pass

    AND

    GIVEN function assigned to default field
    WHEN default is expected function
    THEN it pass
    '''
    valid_function_test_default_method['method']()
    valid_method_test_default_method['method']()


def test_default_invalid_function_value(
        invalid_function_test_default_method,
        invalid_method_test_default_method
):
    '''
    GIVEN method assigned to default field
    WHEN default is not expected method
    THEN it raise exception

    AND

    GIVEN function assigned to default field
    WHEN default is not expected function
    THEN it raise exception
    '''
    with pytest.raises(AssertionError):
        invalid_function_test_default_method['method']()
    with pytest.raises(AssertionError):
        invalid_method_test_default_method['method']()


def test_default_valid_other_value(valid_other_test_default_method):
    '''
    GIVEN value other than method or function assigned to default field
    WHEN default is expected value
    THEN it pass
    '''
    valid_other_test_default_method['method']()


def test_default_invalid_other_value(invalid_other_test_default_method):
    '''
    GIVEN value other than method or function assigned to default field
    WHEN default is not expected value
    THEN it raise exception
    '''
    with pytest.raises(AssertionError):
        invalid_other_test_default_method['method']()

#
#
# validators
#
#


@ pytest.fixture
def prepared_test_validators_method():
    mock = MagicMock()
    method = partial(ModelFieldTest.test_validators, mock)
    return {'method': method, 'mock': mock}


@ pytest.fixture
def empty_test_validators_method(prepared_test_validators_method):
    prepared_test_validators_method['mock'].validators = None
    return prepared_test_validators_method


@ pytest.fixture
def list_test_validators_method(prepared_test_validators_method):
    v = [MagicMock(name='validator_1'), MagicMock(name='validator_2')]
    prepared_test_validators_method['mock'].validators = v
    prepared_test_validators_method['mock'].field.validators = v.copy()
    return prepared_test_validators_method


@ pytest.fixture
def invalid_list_test_validators_method(list_test_validators_method):
    list_test_validators_method['mock'].field.validators.pop()
    print(list_test_validators_method['mock'].field.validators)
    return list_test_validators_method


def test_validators_empty_value(empty_test_validators_method):
    '''
    WHEN validators is None
    THEN it pass
    '''
    empty_test_validators_method['method']()


def test_validators_in_list(list_test_validators_method):
    '''
    WHEN validators are in field validators
    THEN it pass
    '''
    list_test_validators_method['method']()


def test_validators_not_in_list(invalid_list_test_validators_method):
    '''
    WHEN validators are not in field validators
    THEN it raise exception
    '''
    with pytest.raises(AssertionError):
        invalid_list_test_validators_method['method']()
