from typing import Callable
from src.error import FixtureError


def verify_fixtures(func_args_names: list[str], fix_map: dict[str, Callable]):
    "Check if all needed fixtures exists"
    needed_fixtures = set(func_args_names) - set(fix_map)
    if len(needed_fixtures):
        raise FixtureError('Fixtures does not exists', needed_fixtures)
