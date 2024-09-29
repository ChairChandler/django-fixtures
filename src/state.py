from copy import copy
from typing import Callable


class FunctionBackup:
    _instance = None

    def __init__(self):
        self.register = self.register if hasattr(self, 'register') else {}

    @staticmethod
    def _get_key(func: Callable) -> str:
        "Build key from combination of class and method name."
        parts = func.__qualname__.split('.')
        klass_part, func_part = parts[-2], parts[-1]
        return f'{klass_part}.{func_part}'

    def save(self, original: Callable):
        self.register[self._get_key(original)] = copy(original)

    def get(self, wrapper: Callable) -> Callable:
        return self.register[self._get_key(wrapper)]

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FunctionBackup, cls).__new__(cls)
        return cls._instance


def func_copy(wrapper: Callable):
    "Retrieves original function."
    return FunctionBackup().get(wrapper)
