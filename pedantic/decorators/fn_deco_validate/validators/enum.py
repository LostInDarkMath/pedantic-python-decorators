from enum import EnumMeta
from typing import Any

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.exceptions import ValidationError
from pedantic.decorators.fn_deco_validate.validators import Validator


class IsEnum(Validator):
    def __init__(self, enum: EnumMeta) -> None:
        self._enum = enum

    @overrides(Validator)
    def validate(self, value: Any) -> Any:
        try:
            return self._enum(value)
        except (ValueError, TypeError):
            raise ValidationError(f'Incorrect value {value} for enum {self._enum}.')
