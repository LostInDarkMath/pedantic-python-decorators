import os
from typing import Any, Type

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.exceptions import ValidationError
from pedantic.decorators.fn_deco_validate.parameters import ExternalParameter


class EnvironmentVariableParameter(ExternalParameter):
    def __init__(self, name: str, value_type: Type = str) -> None:
        super().__init__(name)

        if value_type not in [str, bool, int, float]:
            raise AssertionError(f'value_type needs to be one of these: str, bool, int & float')

        self._value_type = value_type

    @overrides(ExternalParameter)
    def load_value(self) -> Any:
        if self.name not in os.environ:
            raise ValidationError(f'Environment variable {self.name} was not set.')

        value = os.environ[self.name].strip()

        if self._value_type == bool:
            value = value.lower()
            if value not in ['true', 'false']:
                raise ValidationError(f'Cannot convert {value} to true or false for environment variable {self.name}')

            return value.lower() == 'true'

        return self._value_type(value)
