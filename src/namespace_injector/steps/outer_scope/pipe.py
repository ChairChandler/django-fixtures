from typing import Type, TypeVar

# outer scope
from ._1_ import create_fixtures_getters
from ._2_ import extract_tests_methods
from ._3_ import extract_args_names
from ._4_ import filter_fixtures
from ._5_ import verify_fixtures
# inner scope
from src.namespace_injector.steps.inner_scope import create_wrapper

from src.state import FunctionBackup

T = TypeVar('T')


def inject_fixtures(
    NamespaceClass: Type,
    InjectionClass: Type[T]
) -> Type[T]:
    "Inject fixtures to every `test` method of `InjectionClass`."
    # create object class to get access to properties
    namespace_object = NamespaceClass()

    # get properties from namespace class
    fixtures_getters = create_fixtures_getters(
        NamespaceClass,
        namespace_object
    )
    # get methods with names from desired class
    test_methods = extract_tests_methods(InjectionClass)

    # make fixture injections for every test method
    for (fname, func) in test_methods:
        # get method arguments without self attribute
        func_args_names = extract_args_names(func)

        # set values for fixtures to be used in injector
        fix_maping = filter_fixtures(fixtures_getters, func_args_names)

        # check if all needed fixtures exists
        verify_fixtures(func_args_names, fix_maping)

        # save original function for retrieval/backup
        # method in class has different code, but identical signature
        FunctionBackup().save(func)

        # create wrapper for function
        injector = create_wrapper(func, fix_maping)

        # inject function with fixtures
        setattr(InjectionClass, fname, injector)

    # return modified class with new methods injections
    return InjectionClass
