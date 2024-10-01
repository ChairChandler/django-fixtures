from string import Template
from typing import Callable


CODE_TEMPLATE = Template('''
def $_NEW_FUNC_NAME_($_ARGS_SIGN_):
	return $_OLD_FUNC_NAME_($_ARGS_CALL_)
''')


def build_code_string(
    func_sign: Callable,
    args_sign: list[str],
    func_call: Callable,
    args_call: list[str],
) -> str:
    "Create functin template string from arguments."
    func_name = func_sign.__name__
    args_sign_str = ','.join(args_sign)
    args_call_str = ','.join(args_call)

    method_part = func_call.__qualname__[-1]
    klass_part = func_call.__qualname__[-2]
    func_str = f'{klass_part}.{method_part}'

    code = CODE_TEMPLATE.safe_substitute({
        '_NEW_FUNC_NAME_': func_name,
        '_ARGS_SIGN_': args_sign_str,
        # __qualname__ means full name: <class>.<name> ...
        '_OLD_FUNC_NAME_': func_str,
        '_ARGS_CALL_': args_call_str
    })

    return code
