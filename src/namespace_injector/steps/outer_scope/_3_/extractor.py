import inspect
from typing import Callable


def extract_args_names(func: Callable):
    "Get method arguments without self attribute"
    func_args_names = inspect.getargs(func.__code__)
    func_args_names = func_args_names.args
    func_args_names = filter(lambda x: x != 'self', func_args_names)
    func_args_names = list(func_args_names)
    return func_args_names
