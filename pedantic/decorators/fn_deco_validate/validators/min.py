from typing import Union

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.validators import Validator


class Min(Validator):
    def __init__(self, value: Union[int, float], include_boundary: bool = True) -> None:
        """
            >>> Min(7, True).validate(7)
            7
            >>> Min(7, False).validate(7)  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            ValidatorException: ...
            >>> Min(7, False).validate(7.001)
            7.001
        """
        self._value = value
        self._include_boundary = include_boundary

    @overrides(Validator)
    def validate(self, value: Union[int, float]) -> Union[int, float]:
        if value < self._value and self._include_boundary:
            self.raise_exception(msg=f'smaller then allowed: {value} is not >= {self._value}', value=value)
        elif value <= self._value and not self._include_boundary:
            self.raise_exception(msg=f'smaller then allowed: {value} is not > {self._value}', value=value)

        return value
