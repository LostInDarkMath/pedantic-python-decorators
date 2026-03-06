from uuid import UUID

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.validators import Validator


class IsUuid(Validator): # noqa: D101
    def __init__(self, convert: bool = False) -> None: # noqa: D107
        self._convert = convert

    @overrides(Validator)
    def validate(self, value: str) -> str: # noqa: D102
        try:
            converted_value = UUID(str(value))
        except ValueError:
            return self.raise_exception(msg=f'{value} is not a valid UUID', value=value)

        return converted_value if self._convert else value
