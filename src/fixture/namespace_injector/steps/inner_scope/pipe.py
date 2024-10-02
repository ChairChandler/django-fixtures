from functools import wraps
from typing import Callable
from ._1_ import extract_fixtures
from ._2_ import extract_values
from ._3_ import cleanup_generators


def create_wrapper(func: Callable, fix_maping: dict):
    '''
    Create wrapper for function
    '''
    # copy values from function to nested function
    # to save current reference instead of the last variable reference
    @wraps(func)
    def injector(*args, func=func, fix_maping=fix_maping, **kwargs):
        # unpack fixtures values from properties
        prepared = extract_fixtures(fix_maping)
        # add only values (omit generators)
        only_values = extract_values(prepared)
        # fixtures has lower priority than default test arguments
        only_values.update(kwargs)
        try:
            # run function with fixtures
            ret_val = func(*args, **only_values)
            return ret_val
        finally:
            # cleanup generators (important for memory leakage)
            cleanup_generators(prepared)

    return injector
