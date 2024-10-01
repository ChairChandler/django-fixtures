import inspect
from typing import Type, TypeVar
from fixture.namespace_injector.steps.outer_scope._1_.create_getter import create_getter
from fixture.namespace_injector.steps.outer_scope._1_.getmembers_unsorted import getmembers_unsorted

T = TypeVar('T')


def create_fixtures_getters(NamespaceClass: Type[T], namespace_object: T):
    "Get properties from namespace class"
    return {
        # property name: getter
        # name=name means assign current reference value
        # anonymous function allows to get the latest property value
        name: create_getter(NamespaceClass, namespace_object, name, method)
        # get @property and @cached_property methods
        for (name, method) in getmembers_unsorted(NamespaceClass, [
            inspect.isdatadescriptor,
            inspect.ismethoddescriptor
        ])
        # remove from query set hidden or protected properties
        if not name.startswith('_')
    }
