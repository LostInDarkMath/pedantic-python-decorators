import collections
from typing import Sequence

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.exceptions import ValidationError
from pedantic.decorators.fn_deco_validate.validators.abstract_validator import Validator


class NotEmpty(Validator):
    def __init__(self, strip: bool = True) -> None:
        self.strip = strip

    @overrides(Validator)
    def validate(self, value: Sequence) -> Sequence:
        """
            Throws a ValidationError if the sequence is empty.
            If the sequence is a string, it removes all leading and trailing whitespace.
        """

        if isinstance(value, str):
            if not value.strip():
                raise ValidationError(validator_name=self.name, value=value, message=f'Got empty String which is invalid.')

            return value.strip() if self.strip else value
        elif isinstance(value, collections.Sequence):
            if len(value) == 0:
                raise ValidationError(validator_name=self.name, value=value, message=f'Got empty  which is invalid.')

            return value

        raise ValidationError(validator_name=self.name, value=value, message=f'Got {type(value)} which is not a Sequence.')
