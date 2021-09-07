from typing import Iterable, Iterator, Any

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.validators import Validator


class Composite(Validator):
    def __init__(self, validators: Iterable[Validator]) -> None:
        self._validators = validators

    def __iter__(self) -> Iterator[Validator]:
        for validator in self._validators:
            yield validator

    @overrides(Validator)
    def validate(self, value: Any) -> Any:
        for validator in self:
            validator.validate(value)

        return value
