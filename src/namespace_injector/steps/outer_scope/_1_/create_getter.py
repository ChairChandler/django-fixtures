import inspect
from typing import Generator, Type, Callable, TypeVar, TypedDict
from functools import cached_property


T = TypeVar('T')


class GetterInfo(TypedDict):
    value: object
    generator: Generator[object, None, None] | None


def create_getter(
    namespace_class: Type[T],
    namespace_object: T,
    property_name: str,
    property: property | cached_property
) -> Callable[[], GetterInfo]:
    # check if @property
    if inspect.isdatadescriptor(property):
        accessor = 'fget'
    # check if @cached_property
    elif inspect.ismethoddescriptor(property):
        accessor = 'func'
    else:
        raise ValueError('Invalid method')

    # how to get access to unzip attribute
    # @property: <class>.<method>.fget.unzip
    # @cached_property: <class>.<method>.func.unzip
    A = getattr(namespace_class, property_name)
    A = getattr(A, accessor)

    if hasattr(A, 'unzip'):
        # if property (method in class) is marked using unzip,
        # then unpack it
        return (
            lambda name=property_name: {
                # walrus operator var := val
                'generator': (generator := getattr(namespace_object, name)),
                'value': next(generator)
            }
        )
    else:
        # else just get value
        return (
            lambda name=property_name: {
                'value': (value := getattr(namespace_object, name)),
                'generator': value if isinstance(value, Generator) else None
            }
        )
