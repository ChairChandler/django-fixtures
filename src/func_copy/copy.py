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

    # test self
    if 'self' in map_args.keys() or 'self' in map_args.values():
        raise ValueError('Cannot rename to/from self arg')

    def get_function(replace_function: Callable):
        retrieved = FunctionBackup().get(original_func)

        # get function meta information
        original_signature = inspect.signature(retrieved)

        @wraps(
            replace_function,
            assigned=("__module__", "__name__", "__qualname__", "__doc__")
        )
        def wrapped(*args, **kwargs):
            for name_old, name_new in map_args.items():
                if name_new in kwargs:
                    value = kwargs.pop(name_new)
                    kwargs[name_old] = value
                else:
                    raise ValueError('Argument name does not exists')

            # assign arguments
            bound_args = original_signature.bind_partial(*args, **kwargs)
            return retrieved(**bound_args.arguments)

        # rename arguments names
        new_parameters = []
        for name, param in original_signature.parameters.items():
            if name in map_args:
                new_name = map_args[name]
                param = inspect.Parameter(
                    name=new_name,
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD
                )

            new_parameters.append(param)

        # create new signature
        wrapped_signature = inspect.Signature(new_parameters)

        setattr(wrapped, '__signature__', wrapped_signature)
        return wrapped

    return get_function
