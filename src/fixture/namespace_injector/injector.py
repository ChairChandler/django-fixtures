from functools import partial
from typing import Type, Callable
from .steps.outer_scope import inject_fixtures


# I can't mix pytest fixtures with Django tests easily, I would like also
# to avoid Django fixtures files, so decided to use manual objects access
# to get fixtures workaround.


def use_fixture_namespace(NamespaceClass: Type) -> Callable:
    '''
    Injects fixture into methods arguments from class properties.
    Method must starts with a `test` name.

    Use in inspect module the following predicates for methods:
    - `isdatadescriptor` for `@property` annotated,
    - `ismethoddescriptor` for `@cached_property` annotated

    Example:
    ```
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
    '''
    return partial(inject_fixtures, NamespaceClass)
