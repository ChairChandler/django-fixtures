import pytest
from functools import cached_property
from src import use_fixture_namespace, FixtureError


@pytest.fixture
def example_text():
    return 'some text'


@pytest.fixture
def property_field_type_class(example_text):
    class PropertyFieldClass:
        @property
        def example(self):
            return example_text

    return PropertyFieldClass


@pytest.fixture
def cached_property_field_type_class(example_text):
    class CachedPropertyFieldClass:
        @cached_property
        def example(self):
            return example_text

    return CachedPropertyFieldClass


@pytest.fixture
def unknown_field_type_class():
    class UnknownFieldClass:
        def example(self): pass

    return UnknownFieldClass


def test_property_field_type(property_field_type_class, example_text):
    '''
    GIVEN property field exists in class
    WHEN using it as fixture
    THEN it's return in test (captured by decorator)
    '''
    @use_fixture_namespace(property_field_type_class)
    class ExampleClass:
        def test_method(self, example):
            return example

    tests = ExampleClass()
    assert tests.test_method() == example_text  # type: ignore


def test_cached_property_field_type(
        cached_property_field_type_class,
        example_text
):
    '''
    GIVEN cached property field exists in class
    WHEN using it as fixture
    THEN it's return in test (captured by decorator)
    '''
    @use_fixture_namespace(cached_property_field_type_class)
    class ExampleClass:
        def test_method(self, example):
            return example

    tests = ExampleClass()
    assert tests.test_method() == example_text  # type: ignore


def test_unknown_field_type(unknown_field_type_class):
    '''
    GIVEN other field types exists in class
    WHEN using it as fixture
    THEN it raises exception
    '''
    with pytest.raises(FixtureError) as e:
        @use_fixture_namespace(unknown_field_type_class)
        class ExampleClass:
            def test_method(self, example): pass


def test_invalid_field_type(property_field_type_class):
    '''
    GIVEN property field exists in class
    WHEN using field not existing in fixture namespace
    THEN it raise exception
    '''
    with pytest.raises(FixtureError) as e:
        @use_fixture_namespace(property_field_type_class)
        class ExampleClass:
            def test_method(self, not_existing_fixture): pass


def test_invalid_test_method(property_field_type_class):
    '''
    GIVEN property field exists in class
    WHEN method in test class doesn't starts with a test name
    THEN it raises exception
    '''
    @use_fixture_namespace(property_field_type_class)
    class ExampleClass:
        def normal_method_name(self, example_text): pass

    tests = ExampleClass()
    with pytest.raises(TypeError, match='(missing argument)|(example_text)'):
        tests.normal_method_name()  # type: ignore
