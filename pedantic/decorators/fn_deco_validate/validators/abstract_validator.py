from abc import ABC, abstractmethod
from typing import Any, NoReturn

from pedantic.decorators.fn_deco_validate.exceptions import ValidatorException


class Validator(ABC):
    @abstractmethod
    def validate(self, value: Any) -> Any:
        """
            Validates and convert the value.
            Raises an [ValidatorException] in case of an invalid value.
            To raise this you can simply call self.raise_exception().
        """

    def validate_param(self, value: Any, parameter_name: str) -> Any:
        """
            Validates and converts the value, just like [validate()].
            The difference is that a parameter_name is included in the exception, if an exception is raised.
        """

        try:
            return self.validate(value=value)
        except ValidatorException as ex:
            ex.parameter_name = parameter_name
            raise ex

    def raise_exception(self, value: Any, msg: str) -> NoReturn:
        raise ValidatorException(value=value, validator_name=self.name, msg=msg)

    @property
    def name(self) -> str:
        return self.__class__.__name__
