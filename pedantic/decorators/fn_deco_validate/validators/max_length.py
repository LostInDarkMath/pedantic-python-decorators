import collections
from collections.abc import Sized
from typing import Any

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.validators.abstract_validator import Validator


class MaxLength(Validator):  # noqa: D101
    def __init__(self, length: int) -> None:  # noqa: D107
        self._length = length

    @overrides(Validator)
    def validate(self, value: Sized) -> Any:  # noqa: D102
        if not isinstance(value, collections.abc.Sized):
            self.raise_exception(msg=f'{value} has no length.', value=value)

        if len(value) > self._length:
            self.raise_exception(msg=f'{value} is too long with length {len(value)}.', value=value)

        return value
