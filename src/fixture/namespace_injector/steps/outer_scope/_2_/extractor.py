import inspect
from typing import Type


def extract_tests_methods(InjectionClass: Type):
    "Get methods with names from desired class"
    return [
        (fname, func)
        # get methods
        for (fname, func) in inspect.getmembers(InjectionClass, inspect.isfunction)
        # get only test methods
        if fname.startswith('test')
    ]
