# Description

<style>
  red {
    color: red;
  }
</style>

## Overview

Injects fixture into methods arguments from class properties a.k.a namespace.

Namespace is a class designed to be build on top of properties, `@property` and `@cached_property` annotated methods.

To inject fixtures in a test class, methods in a test class must starts with a `test` name.

Example:

```python
class FixtureNamespace:
    @property
    def words(self):
        return ['a', 'b', 'c']
    @property
    def something(self):
            return self.words + ['d']

@use_fixture_namespace(FixtureNamespace)
class TestClass:
    def test_something(self, words, something):
        assert words == ['a', 'b', 'c']
        assert something == ['a', 'b', 'c', 'd']
```

## Source code

**src** directory contains a single file **base.py**, with a decorator `use_fixture_namespace` designed for injecting properties into test classes from a specified namespace.

## Testing

**tests** directory contains a single file **base_test.py**, with a unit tests for a `use_fixture_namespace` decorator.

To run tests, run script **run_tests.sh** inside **scripts** directory. It will generates unit tests report and coverage report inside **reports** directory.

## Building

To build a package run **run_build.sh** inside **scripts** directory. It will generate **tar.gz** package file inside **dist** directory.

## Installation

Being inside package base directory run
> pip install dist/<red><package_name></red>.whl
