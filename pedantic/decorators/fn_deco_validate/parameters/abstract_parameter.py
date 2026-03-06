from collections.abc import Iterable
from typing import Any, NoReturn

from pedantic.decorators.fn_deco_validate.convert_value import convert_value
from pedantic.decorators.fn_deco_validate.exceptions import ConversionError, ParameterException, ValidatorException
from pedantic.decorators.fn_deco_validate.validators.abstract_validator import Validator


class NoValue:
    """An alternative to None."""


class Parameter:  # noqa: D101
    exception_type: type[ParameterException] = ParameterException

    def __init__(  # noqa: D107
        self,
        name: str,
        value_type: type[bool | int | float | str | dict | list] | None = None,
        validators: Iterable[Validator] | None = None,
        default: Any = NoValue,
        required: bool = True,
     ) -> None:
        self.name = name
        self.validators = validators or []
        self.default_value = default
        self.value_type = value_type
        self.is_required = False if default != NoValue else required

        if value_type not in [str, bool, int, float, dict, list, None]:
            raise AssertionError('value_type needs to be one of these: str, bool, int, float, dict & list')

    def validate(self, value: Any) -> Any:
        """Apply all validators to the given value and collect all ValidationErrors."""

        if value is None:
            if self.is_required:
                self.raise_exception(msg=f'Value for key {self.name} is required.')

            return None

        if self.value_type is not None:
            try:
                result_value = convert_value(value=value, target_type=self.value_type)
            except ConversionError as ex:
                return self.raise_exception(value=value, msg=ex.message)
        else:
            result_value = value

        for validator in self.validators:
            try:
                result_value = validator.validate(result_value)
            except ValidatorException as e:
                raise self.exception_type.from_validator_exception(exception=e, parameter_name=self.name) from e

        return result_value

    def raise_exception(self, msg: str, value: Any = None, validator: Validator | None = None) -> NoReturn:  # noqa: D102
        raise self.exception_type(value=value, parameter_name=self.name, msg=msg,
                                  validator_name=validator.name if validator else None)

    def __str__(self) -> str:
        return self.__class__.__name__ + ' name=' + self.name
