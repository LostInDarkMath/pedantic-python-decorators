import collections
from typing import Any, Iterable, List, Union

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.validators import Validator


class ForEach(Validator):
    def __init__(self, validators: Union[Validator, Iterable[Validator]]) -> None:
        if isinstance(validators, Validator):
            self._validators = [validators]
        else:
            self._validators = validators

    @overrides(Validator)
    def validate(self, value: Iterable[Any]) -> List[Any]:
        if not isinstance(value, collections.abc.Iterable):
            self.raise_exception(msg=f'{value} is not iterable.', value=value)

        results = []

        for item in value:
            for validator in self._validators:
                item = validator.validate(item)

            results.append(item)

        return results
