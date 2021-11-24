import os
from typing import Any, Type, Iterable, Union

from pedantic.decorators.fn_deco_overrides import overrides
from pedantic.decorators.fn_deco_validate.parameters import ExternalParameter
from pedantic.decorators.fn_deco_validate.parameters.abstract_parameter import NoValue
from pedantic.decorators.fn_deco_validate.validators import Validator


class EnvironmentVariableParameter(ExternalParameter):
    def __init__(self,
                 name: str,
                 env_var_name: str = None,
                 value_type: Type[Union[str, bool, int, float]] = str,
                 validators: Iterable[Validator] = None,
                 required: bool = True,
                 default: Any = NoValue,
                 ) -> None:
        super().__init__(name=name, validators=validators, default=default, value_type=value_type, required=required)

        if value_type not in [str, bool, int, float]:
            raise AssertionError(f'value_type needs to be one of these: str, bool, int & float')

        if env_var_name is None:
            self._env_var_name = name
        else:
            self._env_var_name = env_var_name

    @overrides(ExternalParameter)
    def has_value(self) -> bool:
        return self._env_var_name in os.environ

    @overrides(ExternalParameter)
    def load_value(self) -> Any:
        return os.environ[self._env_var_name].strip()
