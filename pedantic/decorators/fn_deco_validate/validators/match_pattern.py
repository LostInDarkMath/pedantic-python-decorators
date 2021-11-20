import re

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.validators import Validator


class MatchPattern(Validator):
    def __init__(self, pattern: str) -> None:
        self._pattern = re.compile(pattern=pattern)

    @overrides(Validator)
    def validate(self, value: str) -> str:
        if not self._pattern.search(string=str(value)):
            self.raise_exception(msg=f'Value "{value}" does not match pattern {self._pattern.pattern}.', value=value)

        return value
