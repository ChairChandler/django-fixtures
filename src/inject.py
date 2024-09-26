import inspect
from typing import Type, Callable
from functools import wraps

# I can't mix pytest fixtures with Django tests easily, I would like also
# to avoid Django fixtures files, so decided to use manual objects access
# to get fixtures workaround.


class FixtureError(KeyError):
    pass


def getmembers_unsorted(object, predicates: list):
    # http://192.168.2.1:3000/alewandowski/django-fixtures/issues/4
    return [
        (name, member)
        for (name, member) in object.__dict__.items()
        if any(p(member) for p in predicates)
    ]


def create_getter(namespace_class, namespace_object, property_name, property):
    # check if @property
    if inspect.isdatadescriptor(property):
        accessor = 'fget'
    # check if @cached_property
    elif inspect.ismethoddescriptor(property):
        accessor = 'func'
    else:
        raise ValueError('Invalid method')

    # how to get access to unzip attribute
    # @property: <class>.<method>.fget.unzip
    # @cached_property: <class>.<method>.func.unzip
    A = getattr(namespace_class, property_name)
    A = getattr(A, accessor)

    if hasattr(A, 'unzip'):
        # if property (method in class) is marked using unzip,
        # then unpack it
        return (
            lambda name=property_name:
                next(getattr(namespace_object, name))
        )
    else:
        # else just get value
        return (
            lambda name=property_name:
                getattr(namespace_object, name)
        )


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
            name: create_getter(NamespaceClass, namespace_object, name, method)
            # get @property and @cached_property methods
            for (name, method) in getmembers_unsorted(NamespaceClass, [
                inspect.isdatadescriptor,
                inspect.ismethoddescriptor
            ])
            # remove from query set hidden or protected properties
            if not name.startswith('_')
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
            func_args_names = list(func_args_names)

            # set values for fixtures to be used in injector
            fix_map = {
                prop_name: getter
                # we have to iterate over namespace class to have
                # exactly the same order of injecting properties
                # from top to bottom
                for (prop_name, getter) in fixtures_getters.items()
                if prop_name in func_args_names
            }
            # get needed fixtures not existed in namespace class
            needed_fixtures = set(func_args_names) - set(fix_map)
            if len(needed_fixtures):
                raise FixtureError('Fixture does not exists')

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
