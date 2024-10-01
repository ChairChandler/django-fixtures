from functools import wraps
from typing import Callable
import inspect

from src.state import FunctionBackup
from .steps._1_.extractor import extract_arguments
from .steps._2_.builder import build_code_string
from .steps._3_.compiler import compile_function


def func_copy(original_func: Callable, map_args: dict[str, str] = {}):
    '''
    Copy `original_func` code and injects into current function.

    Example:
    ```
    @use_fixture_namespace(Namespace_X)
    class X:
        def test_something(self, x, y): ...

    @use_fixture_namespace(Namespace_Y)
    class Y:
        @func_copy(
            X.test_something,
            map_args={
                'x': 'z'
            }
        )
        def test_different(self): ...
    ```

    which will produce the following internal code:
    ```
    @use_fixture_namespace(Namespace_Y)
    class Y:
        def test_different(self, z, y):
            return X.test_something(self, z, y)
    ```
    '''
    # we have to load objects from previous calling file
    # because every file has different globals()
    last_file = inspect.currentframe().f_back  # type: ignore
    objects_to_load = (
        last_file.f_globals,  # type: ignore
        last_file.f_locals  # type: ignore
    )

    def wrapper(replace_function: Callable):
        retrieved = FunctionBackup().get(original_func)

        # get function meta information
        signature = inspect.signature(retrieved)

        args_call, args_sign = extract_arguments(signature, map_args)

        code = build_code_string(
            func_sign=replace_function,
            args_sign=args_sign,
            func_call=retrieved,
            args_call=args_call
        )

        new_func = compile_function(
            code=code,
            func_name=replace_function.__name__,
            objects_to_load=objects_to_load
        )
        # keep meta attributes of original function
        new_func = wraps(replace_function)(new_func)
        return new_func
    return wrapper
