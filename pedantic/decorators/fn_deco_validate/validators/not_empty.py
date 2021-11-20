import collections
from typing import Sequence

from pedantic import overrides
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
                self.raise_exception(msg=f'Got empty String which is invalid.', value=value)

            return value.strip() if self.strip else value
        elif isinstance(value, collections.abc.Sequence):
            if len(value) == 0:
                raise self.raise_exception(msg=f'Got empty  which is invalid.', value=value)

            return value

        self.raise_exception(msg=f'Got {type(value)} which is not a Sequence.', value=value)
