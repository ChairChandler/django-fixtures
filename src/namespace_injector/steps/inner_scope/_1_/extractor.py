from typing import Callable

from src.steps.outer_scope._1_.create_getter import GetterInfo


def extract_fixtures(fix_maping: dict[str, Callable]) -> dict[str, GetterInfo]:
    "Unpack fixtures values from properties"
    return {
        fixture_name: getter()
        for fixture_name, getter in fix_maping.items()
        if getter
    }
