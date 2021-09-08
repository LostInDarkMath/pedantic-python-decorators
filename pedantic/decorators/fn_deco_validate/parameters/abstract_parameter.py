from typing import Iterable, Any, Type, Union

from pedantic.decorators.fn_deco_validate.convert_value import convert_value
from pedantic.decorators.fn_deco_validate.exceptions import ValidationError, ValidateException
from pedantic.decorators.fn_deco_validate.validators.abstract_validator import Validator


class Parameter:
    exception_type: Type[Exception] = ValidateException

    def __init__(self,
                 name: str,
                 value_type: Type[Union[bool, int, float, str, dict, list]] = None,
                 validators: Iterable[Validator] = None,
                 default: Any = None,
                 required: bool = True,
                 ) -> None:
        self.name = name
        self.validators = validators if validators else []
        self.default_value = default
        self.value_type = value_type
        self.is_required = required

        if value_type not in [str, bool, int, float, dict, list, None]:
            raise AssertionError(f'value_type needs to be one of these: str, bool, int, float, dict & list')

    def validate(self, value: Any) -> Any:
        """ Apply all validators to the given value and collect all ValidationErrors. """

        if value is None:
            if self.is_required:
                raise self.exception_type(f'Value for key {self.name} is required.')

            return None

        if self.value_type is not None:
            result_value = convert_value(value=value, target_type=self.value_type)
        else:
            result_value = value

        for validator in self.validators:
            try:
                result_value = validator.validate(result_value)
            except ValidationError as e:
                e.validator_name = validator.name
                e.value = value
                raise e

        return result_value

    def __str__(self) -> str:
        return self.__class__.__name__ + ' name=' + self.name
