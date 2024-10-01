# Description

<style>
  red {
    color: red;
  }
</style>

## Overview

Injects fixture into methods arguments from class properties a.k.a namespace.

Namespace is a class designed to be build on top of properties, `@property` and `@cached_property` annotated methods.

To inject fixtures in a test class, methods in a test class must starts with a `test` name. Fixtures are loaded in namespace class definition order.

`@unzip` decorator allows to load generator/mock directly without calling `next(mock)` on it. All generators (marked with **unzip** or without) are automatically closed after test is done.

Tests can be copy using `func_copy` function.

Example:

```python
class FixtureNamespace:
    @property
    def words(self):
        return ['a', 'b', 'c']

    @cached_property
    def something(self):
            return self.words + ['d']
    
    @property # or @cached_property
    @fixture.unzip
    def mock(self):
      with patch('path.to.Mock') as mock:
        yield mock

@fixture.use_fixture_namespace(FixtureNamespace)
class TestClass:
    def test_words(self, words):
        assert words == ['a', 'b', 'c']

    def test_something(self, something, mock):
        assert something == ['a', 'b', 'c', 'd']
        assert isinstance(mock, Mock)

class AnotherNamespace:
    @property
    def words(self):
        return ['X', 'Y']

    @property
    def something(self):
      return 'xyz'

    @property
    def new_mock_name(self):
      return 123

@fixture.use_fixture_namespace(AnotherNamespace)
class AnotherClass:
    @fixture.func_copy(
      TestClass.test_words
    )
    def test_copy_1(self): 
      pass

    @fixture.func_copy(
      TestClass.test_something,
      map_args={'mock': 'new_mock_name'}
    )
    def test_copy_2(self): 
      pass
```

## Source code

**src** directory contains a single file **base.py**, with a decorator `use_fixture_namespace` designed for injecting properties into test classes from a specified namespace.

## Testing

**tests** directory contains a single file **base_test.py**, with a unit tests for a `use_fixture_namespace` decorator.

To run tests, run script **run_tests.sh** inside **scripts** directory. It will generates unit tests report and coverage report inside **reports** directory.

## Building

To build a package run **run_build.sh** inside **scripts** directory. It will generate **whl** package file inside **dist** directory.

## Installation

Being inside package base directory run
> pip install dist/<red><package_name></red>.whl
