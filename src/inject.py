import inspect
from typing import Type, Callable
from functools import wraps

# I can't mix pytest fixtures with Django tests easily, I would like also
# to avoid Django fixtures files, so decided to use manual objects access
# to get fixtures workaround.


class FixtureError(KeyError):
    pass


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
    # create object class to get access to properties
    namespace_object = NamespaceClass()

    def inject_fixtures(InjectionClass: Type) -> Type:
        "Inject fixtures to every `test` method of `InjectionClass`."
        # get properties from namespace class
        fixtures_getters = {
            # property name: getter
            # name=name means assign current reference value
            # anonymous function allows to get the latest property value
            #
            #
            # FOR @property
            **{
                name: (
                    # if property (method in class) is marked using unzip,
                    # then unpack it
                    lambda name=name: next(getattr(namespace_object, name))
                    # how to get access
                    # @property: <class>.<method>.fget.unzip
                    if hasattr(getattr(NamespaceClass, name).fget, 'unzip')
                    # else just get value
                    else getattr(namespace_object, name)
                )
                # get @property methods
                for (name, _) in inspect.getmembers(NamespaceClass, inspect.isdatadescriptor)
                # remove from query set hidden or protected properties
                if not name.startswith('_')
            },
            # FOR @cached_property
            **{
                name: (
                    # if property (method in class) is marked using unzip,
                    # then unpack it
                    lambda name=name: next(getattr(namespace_object, name))
                    # how to get access
                    # @cached_property: <class>.<method>.func.unzip
                    if hasattr(getattr(NamespaceClass, name).func, 'unzip')
                    # else just get value
                    else getattr(namespace_object, name)
                )
                for (name, _) in inspect.getmembers(NamespaceClass, inspect.ismethoddescriptor)
                # remove from query set hidden or protected properties
                if not name.startswith('_')
            }
        }

        # get methods with names from desired class
        test_methods = [
            (fname, func)
            # get methods
            for (fname, func) in inspect.getmembers(InjectionClass, inspect.isfunction)
            # get only test methods
            if fname.startswith('test')
        ]

        # make fixture injections for every test method
        for (fname, func) in test_methods:
            # get method arguments without self attribute
            func_args_names = inspect.getargs(func.__code__)
            func_args_names = func_args_names.args
            func_args_names = filter(lambda x: x != 'self', func_args_names)

            # set values for fixtures to be used in injector
            try:
                fix_map = {a: fixtures_getters[a] for a in func_args_names}
            except KeyError as e:
                raise FixtureError('Fixture does not exists') from e

            # create wrapper for function
            # copy values from function to nested function
            # to save current reference instead of the last variable reference
            @wraps(func)
            def injector(*args, func=func, fix_map=fix_map, **kwargs):
                # unpack fixtures values from properties
                prepared = {
                    fixture_name: getter()
                    for fixture_name, getter in fix_map.items()
                    if getter
                }
                kwargs.update(prepared)
                # run function with fixtures
                return func(*args, **kwargs)

            # inject function with fixtures
            setattr(InjectionClass, fname, injector)

        # return modified class with new methods injections
        return InjectionClass

    return inject_fixtures
