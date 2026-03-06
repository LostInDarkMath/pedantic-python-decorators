import re

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.validators import Validator


class MatchPattern(Validator):  # noqa: D101
    def __init__(self, pattern: str) -> None:  # noqa: D107
        self._pattern = re.compile(pattern=pattern)

    @overrides(Validator)
    def validate(self, value: str) -> str: # noqa: D102
        if not self._pattern.search(string=str(value)):
            self.raise_exception(msg=f'Value "{value}" does not match pattern {self._pattern.pattern}.', value=value)

        return value
