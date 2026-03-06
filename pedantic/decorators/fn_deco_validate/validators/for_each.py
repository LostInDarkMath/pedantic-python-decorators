import collections
from collections.abc import Iterable
from typing import Any

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.validators import Validator


class ForEach(Validator):  # noqa: D101
    def __init__(self, validators: Validator | Iterable[Validator]) -> None:  # noqa: D107
        if isinstance(validators, Validator):
            self._validators = [validators]
        else:
            self._validators = validators

    @overrides(Validator)
    def validate(self, value: Iterable[Any]) -> list[Any]:  # noqa: D102
        if not isinstance(value, collections.abc.Iterable):
            self.raise_exception(msg=f'{value} is not iterable.', value=value)

        results = []

        for item in value:
            for validator in self._validators:
                item = validator.validate(item)  # noqa: PLW2901

            results.append(item)

        return results
