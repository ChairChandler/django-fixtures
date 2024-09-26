import pytest
from functools import cached_property
from src import use_fixture_namespace, FixtureError
from src.unzip import unzip


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


@pytest.fixture
def property_field_unzip_marked(example_text):
    class PropertyFieldClass:
        @property
        @unzip
        def example(self):
            yield example_text

        @cached_property
        @unzip
        def example_cache(self):
            yield example_text

    return PropertyFieldClass


@pytest.fixture
def property_field_loading_in_order():
    class PropertyFieldClass:
        msg = []

        @property
        def value_2(self):
            PropertyFieldClass.msg.append('BEFORE')
            return PropertyFieldClass.msg.copy()

        @property
        def value_1(self):
            PropertyFieldClass.msg.append('AFTER')
            return PropertyFieldClass.msg.copy()

    return PropertyFieldClass


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
    # arguments already injected
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


def test_property_marked_using_unzip(property_field_unzip_marked):
    '''
    GIVEN property field in class marked with unzip decorator
    WHEN check if property has 'unzip' attribute
    THEN result is True
    '''
    assert hasattr(property_field_unzip_marked.example.fget, 'unzip')
    assert hasattr(property_field_unzip_marked.example_cache.func, 'unzip')


def test_unzip_marked_property(property_field_unzip_marked, example_text):
    '''
    GIVEN property field in class marked with unzip decorator
    WHEN injecting this field
    THEN field is injected with yield value
    '''
    @use_fixture_namespace(property_field_unzip_marked)
    class ExampleClass:
        def test_method(self, example):
            return example

        def test_method_cache(self, example_cache):
            return example_cache

    tests = ExampleClass()
    assert tests.test_method() == example_text  # type: ignore
    assert tests.test_method_cache() == example_text  # type: ignore


def test_loading_in_order(property_field_loading_in_order):
    '''
    GIVEN property fields in class
    WHEN injecting fields
    THEN fields injected in order by class definition
    '''
    @use_fixture_namespace(property_field_loading_in_order)
    class ExampleClass:
        def test_1(self, value_1, value_2):
            return value_2, value_1

        def test_2(self, value_2, value_1):
            return value_2, value_1

    tests = ExampleClass()

    args = tests.test_1()  # type: ignore
    assert args == (['BEFORE'], ['BEFORE', 'AFTER'])

    args = tests.test_2()  # type: ignore
    assert args == (['BEFORE', 'AFTER', 'BEFORE'], [
                    'BEFORE', 'AFTER', 'BEFORE', 'AFTER'])
