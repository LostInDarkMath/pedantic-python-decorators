from collections.abc import Iterable, Iterator
from typing import Any

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.validators import Validator


class Composite(Validator): # noqa: D101
    def __init__(self, validators: Iterable[Validator]) -> None:  # noqa: D107
        self._validators = validators

    def __iter__(self) -> Iterator[Validator]:
        yield from self._validators

    @overrides(Validator)
    def validate(self, value: Any) -> Any: # noqa: D102
        for validator in self:
            validator.validate(value)

        return value
