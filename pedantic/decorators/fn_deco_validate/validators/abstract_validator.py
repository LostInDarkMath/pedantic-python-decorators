from abc import ABC, abstractmethod
from typing import Any


class Validator(ABC):
    @abstractmethod
    def validate(self, value: Any) -> Any:
        """
            Validates and convert the value.
            Raises an ValidationError in case of an invalid value.
        """

    @property
    def name(self) -> str:
        return self.__class__.__name__
