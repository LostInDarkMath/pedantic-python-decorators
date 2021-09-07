import os
from typing import Any, Type, Iterable

from pedantic.decorators.fn_deco_overrides import overrides
from pedantic.decorators.fn_deco_validate.exceptions import ValidationError
from pedantic.decorators.fn_deco_validate.parameters import ExternalParameter
from pedantic.decorators.fn_deco_validate.validators import Validator


class EnvironmentVariableParameter(ExternalParameter):
    def __init__(self,
                 name: str,
                 env_var_name: str = None,
                 value_type: Type = str,
                 validators: Iterable[Validator] = None,
                 default: Any = None,
                 ) -> None:
        super().__init__(name=name, validators=validators, default=default)

        if value_type not in [str, bool, int, float]:
            raise AssertionError(f'value_type needs to be one of these: str, bool, int & float')

        self._value_type = value_type

        if env_var_name is None:
            self._env_var_name = name
        else:
            self._env_var_name = env_var_name

    @overrides(ExternalParameter)
    def load_value(self) -> Any:
        if self._env_var_name not in os.environ:
            raise ValidationError(f'Environment variable {self._env_var_name} was not set.')

        value = os.environ[self._env_var_name].strip()

        if self._value_type == bool:
            value = value.lower()

            if value not in ['true', 'false']:
                raise ValidationError(f'Cannot convert {value} to true or false for environment variable '
                                      f'{self._env_var_name}')

            return value.lower() == 'true'

        return self._value_type(value)
