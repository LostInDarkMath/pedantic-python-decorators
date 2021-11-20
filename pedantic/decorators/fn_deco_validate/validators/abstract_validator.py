from abc import ABC, abstractmethod
from typing import Any, NoReturn

from pedantic.decorators.fn_deco_validate.exceptions import ValidatorException


class Validator(ABC):
    @abstractmethod
    def validate(self, value: Any) -> Any:
        """
            Validates and convert the value.
            Raises an ValidationError in case of an invalid value.
        """

    def raise_exception(self, value: Any, msg: str) -> NoReturn:
        raise ValidatorException(value=value, validator_name=self.name, msg=msg)

    @property
    def name(self) -> str:
        return self.__class__.__name__
