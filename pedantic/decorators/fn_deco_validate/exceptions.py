from typing import Any


class ExceptionDictKey: # noqa: D101
    VALUE = 'VALUE'
    MESSAGE = 'MESSAGE'
    PARAMETER = 'PARAMETER'
    VALIDATOR = 'VALIDATOR'


class ValidateException(Exception):  # noqa: N818
    """The base class for all exception thrown by the validate decorator."""

    def __init__(self, msg: str) -> None: # noqa: D107
        self.message = msg


class ValidatorException(ValidateException):
    """An exception that is raised inside the validate() function of a Validator."""

    def __init__(self, msg: str, validator_name: str, value: Any, parameter_name: str = '') -> None: # noqa: D107
        super().__init__(msg=msg)
        self.validator_name = validator_name
        self.value = value
        self.parameter_name = parameter_name

    def __str__(self) -> str:
        return f'{self.validator_name}: {self.message} Value: {self.value}'


class ParameterException(ValidateException):
    """An exception that is raised inside a Parameter."""

    def __init__( # noqa: D107
        self,
        msg: str,
        parameter_name: str,
        value: Any | None = None,
        validator_name: str | None = None,
    ) -> None:
        super().__init__(msg=msg)
        self.validator_name = validator_name
        self.parameter_name = parameter_name
        self.value = value

    @classmethod
    def from_validator_exception(cls, exception: ValidatorException, parameter_name: str = '') -> 'ParameterException':
        """Creates a parameter exception from a validator exception."""
        return cls(
            value=exception.value,
            msg=exception.message,
            validator_name=exception.validator_name,
            parameter_name=parameter_name or exception.parameter_name,
        )

    def __str__(self) -> str:
        return str(self.to_dict)

    @property
    def to_dict(self) -> dict[str, str]:  # noqa: D102
        return {
            ExceptionDictKey.VALUE: str(self.value),
            ExceptionDictKey.MESSAGE: self.message,
            ExceptionDictKey.VALIDATOR: self.validator_name,
            ExceptionDictKey.PARAMETER: self.parameter_name,
        }


class InvalidHeader(ParameterException):
    """Is raised if there is a validation error in a FlaskHeaderParameter."""


class TooManyArguments(ValidateException):
    """Is raised if the function got more arguments than expected."""


class ConversionError(ValidateException):
    """Is raised if a type cast failed."""
