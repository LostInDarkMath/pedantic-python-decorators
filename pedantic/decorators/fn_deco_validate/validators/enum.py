from enum import EnumMeta, IntEnum
from typing import Any

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.validators import Validator


class IsEnum(Validator):
    def __init__(self, enum: EnumMeta, convert: bool = True, to_upper_case: bool = True) -> None:
        self._enum = enum
        self._convert = convert
        self._to_upper_case = to_upper_case

    @overrides(Validator)
    def validate(self, value: Any) -> Any:
        try:
            if isinstance(value, str) and self._to_upper_case:
                value = value.upper()

            if issubclass(self._enum, IntEnum):
                enum_value = self._enum(int(value))
            else:
                enum_value = self._enum(value)
        except (ValueError, TypeError):
            return self.raise_exception(msg=f'Incorrect value {value} for enum {self._enum}.', value=value)

        if self._convert:
            return enum_value

        return value
