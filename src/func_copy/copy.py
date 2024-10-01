from functools import wraps
from typing import Callable
import inspect

from src.state import FunctionBackup


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

    def get_function(replace_function: Callable):
        retrieved = FunctionBackup().get(original_func)

        # get function meta information
        signature = inspect.signature(retrieved)

        @wraps(
            replace_function,
            assigned=("__module__", "__name__", "__qualname__", "__doc__")
        )
        def wrapped(*args, **kwargs):
            print(args)
            print(kwargs)
            # assign arguments
            bound_args = signature.bind_partial(*args, **kwargs)

            # rename arguments names
            for old_arg, new_arg in map_args.items():
                if old_arg in bound_args.arguments:
                    value = bound_args.arguments.pop(old_arg)
                    bound_args.arguments[new_arg] = value

            return retrieved(**bound_args.arguments)

        # get function meta information
        signature = inspect.signature(wrapped)
        setattr(wrapped, '__signature__', signature)
        return wrapped

    return get_function
