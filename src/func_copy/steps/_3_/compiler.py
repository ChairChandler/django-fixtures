from typing import Callable


def compile_function(
    code: str,
    func_name: str,
    objects_to_load: tuple
) -> Callable:
    "Create function from string in current python runtime."
    # copy objects from importing decorator modules
    # and injects into current file globals
    # to pass compilation for arguments with default values
    for objects in objects_to_load:
        globals().update(objects)
    # run with imported objects
    exec(code, globals())
    new_func: Callable = globals().get(func_name)  # type: ignore
    return new_func
