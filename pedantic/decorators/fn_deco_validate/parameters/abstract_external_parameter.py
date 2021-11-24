from abc import ABC, abstractmethod
from typing import Any

from pedantic.decorators.fn_deco_validate.parameters.abstract_parameter import Parameter


class ExternalParameter(Parameter, ABC):
    @abstractmethod
    def has_value(self) -> bool:
        """ Returns True if the value can be fetched. """

    @abstractmethod
    def load_value(self) -> Any:
        """Loads a value and returns it."""
