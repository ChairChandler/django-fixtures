import inspect


def extract_arguments(signature: inspect.Signature, map_args: dict):
    "Extracts function arguments and convert their name if required."
    # args_call = ['x', 'y', 'z'] => var = func(x, y, z)
    args_call = []
    # args_sign = ['x', 'y', 'z'] => def func(x, y, z)
    args_sign = []
    # for each function argument
    for param in signature.parameters.values():
        # replace argument name if possible
        if (value := map_args.get(param.name)):
            param = param.replace(name=value)

        args_call.append(param.name)
        # make arg name with default value if possible
        param_str = (
            f'{param.name}={param.default}'
            if param.default != inspect._empty
            else
            param.name
        )
        args_sign.append(param_str)

    return args_call, args_sign
