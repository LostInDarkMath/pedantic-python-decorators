from typing import Union

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.validators import Validator


class Max(Validator):
    def __init__(self, value: Union[int, float], include_boundary: bool = True) -> None:
        """
            >>> Max(7, True).validate(7)
            True
            >>> Max(7, False).validate(7)
            False
            >>> Max(7, False).validate(6.999)
            True
        """
        self._value = value
        self._include_boundary = include_boundary

    @overrides(Validator)
    def validate(self, value: Union[int, float]) -> Union[int, float]:
        if value > self._value and self._include_boundary:
            self.raise_exception(msg=f'greater then allowed: {value} is not <= {self._value}', value=value)
        elif value >= self._value and not self._include_boundary:
            self.raise_exception(msg=f'greater then allowed: {value} is not < {self._value}', value=value)

        return value
