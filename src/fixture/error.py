from typing import Iterable


class FixtureError(KeyError):
    def __init__(self, msg: str, fixtures: Iterable[str]) -> None:
        super().__init__(msg)
        self.msg = msg
        self.fixtures = fixtures

    def __str__(self) -> str:
        fix_str = ', '.join([fix for fix in self.fixtures])
        return f'{self.msg}: {fix_str}'
