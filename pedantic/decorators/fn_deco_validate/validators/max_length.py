import collections
from typing import Sized, Any

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.exceptions import ValidationError
from pedantic.decorators.fn_deco_validate.validators.abstract_validator import Validator


class MaxLength(Validator):
    def __init__(self, length: int) -> None:
        self._length = length

    @overrides(Validator)
    def validate(self, value: Sized) -> Any:
        if not isinstance(value, collections.Sized):
            raise ValidationError(validator_name=self.name, value=value, message=f'{value} has no length.')

        if len(value) > self._length:
            raise ValidationError(validator_name=self.name, value=value, message=f'{value} is too long with length {len(value)}.')

        return value
