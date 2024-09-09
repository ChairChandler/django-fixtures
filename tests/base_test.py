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
        def another_example(self):
            return example_text

    return CachedPropertyFieldClass


@pytest.fixture
def unknown_field_type_class():
    class UnknownFieldClass:
        def normal_method(self): pass

    return UnknownFieldClass


def test_property_field_type(property_field_type_class, example_text):
    '''
    WHEN property field exists in class
    THEN use it as fixture
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
    WHEN property field exists in class
    THEN use it as fixture
    '''
    @use_fixture_namespace(cached_property_field_type_class)
    class ExampleClass:
        def test_method(self, another_example):
            return another_example

    tests = ExampleClass()
    assert tests.test_method() == example_text  # type: ignore


def test_unknown_field_type(unknown_field_type_class):
    '''
    WHEN other field types exists in class
    THEN do nothing with them
    '''
    with pytest.raises(FixtureError) as e:
        @use_fixture_namespace(unknown_field_type_class)
        class ExampleClass:
            def test_method(self, another_example): pass


def test_invalid_test_method(property_field_type_class):
    '''
    WHEN method in test class doesn't starts with a test name
    THEN do nothing with it
    '''
    @use_fixture_namespace(property_field_type_class)
    class ExampleClass:
        def normal_method_name(self, example_text): pass

    tests = ExampleClass()
    with pytest.raises(TypeError, match='(missing argument)|(example_text)'):
        tests.normal_method_name()  # type: ignore
