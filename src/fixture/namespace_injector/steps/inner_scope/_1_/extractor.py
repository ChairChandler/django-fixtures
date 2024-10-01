from typing import Callable

from fixture.namespace_injector.steps.outer_scope._1_ import GetterInfo


def extract_fixtures(fix_maping: dict[str, Callable]) -> dict[str, GetterInfo]:
    "Unpack fixtures values from properties"
    return {
        fixture_name: getter()
        for fixture_name, getter in fix_maping.items()
        if getter
    }
