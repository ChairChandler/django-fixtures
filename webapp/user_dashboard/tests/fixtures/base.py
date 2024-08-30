import inspect
from functools import wraps
from typing import Type, Callable


def use_fixture_namespace(namespace_class: Type) -> Callable:
    '''
    Injects fixture into methods arguments from class properties.

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

    T = namespace_class()

    def inject_fixtures(destination_class: Type) -> Type:
        # get properties from class
        fixtures = {
            name: getattr(T, name)
            for (name, _) in inspect.getmembers(namespace_class, inspect.isdatadescriptor)
            # remove from query set hidden or protected properties
            if not name.startswith('_') and not name.endswith('_')
        }
        # get methods and methods-args from desired class
        for (fname, func) in inspect.getmembers(destination_class, inspect.isfunction):
            # get method arguments without self attribute
            args = inspect.getargs(func.__code__).args
            args = filter(lambda x: x != 'self', args)

            # set values for fixtures to be used in injector
            fix_map = {}
            for a in args:
                arg_value = fixtures.get(a, None)
                fix_map[a] = arg_value

            # create wrapper for function
            @wraps(func)
            def injector(*args, **kwargs):
                return func(*args, **fix_map, **kwargs)

            # inject function with fixtures
            setattr(destination_class, fname, injector)

        return destination_class

    return inject_fixtures
