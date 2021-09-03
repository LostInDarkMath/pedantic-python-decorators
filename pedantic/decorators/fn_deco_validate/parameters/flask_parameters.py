from abc import ABC, abstractmethod
from typing import Any, Type, List, Dict

from flask import request

from pedantic.decorators.fn_deco_overrides import overrides
from pedantic.decorators.fn_deco_validate.exceptions import ValidationError
from pedantic.decorators.fn_deco_validate.parameters import ExternalParameter, Parameter
from pedantic.decorators.fn_deco_validate.validators import Validator


class FlaskParameter(ExternalParameter, ABC):
    def __init__(
            self,
            name: str,
            validators: List[Validator] = None,
            value_type: Type = None,
            required: bool = True,
            default: Any = None,
    ):
        super().__init__(name, validators)

        if value_type not in [str, bool, int, float, dict, list, None]:
            raise AssertionError(f'value_type needs to be one of these: str, bool, int, float, dict & list')

        self._value_type = value_type
        self._required = required
        self._default = default

    @abstractmethod
    def get_dict(self) -> Dict[str, Any]:
        """ Returns the actual values as a dictionary. """

    @overrides(ExternalParameter)
    def load_value(self) -> Any:
        value = self._load_value()

        if self._value_type is None or isinstance(value, self._value_type):
            return value

    def _load_value(self) -> Any:
        dict_ = self.get_dict()

        if self.name in dict_ and dict_[self.name] is not None:
            return dict_[self.name]

        if self._default is not None:
            return self._default

        if self._required:
            raise ValidationError(f'Value for key {self.name} is required.')

        return None


class FlaskJsonParameter(FlaskParameter):
    @overrides(FlaskParameter)
    def get_dict(self) -> Dict:
        return request.json


class FlaskFormParameter(FlaskParameter):
    @overrides(FlaskParameter)
    def get_dict(self) -> Dict:
        return request.form


class FlaskPathParameter(Parameter):
    """
    This is a special case because Flask passes path parameter as kwargs to validate().
    Therefore, this doesn't need to be an ExternalParameter.
    """


class FlaskGetParameter(FlaskParameter):
    @overrides(FlaskParameter)
    def get_dict(self) -> Dict:
        return request.args


class FlaskHeaderParameter(FlaskParameter):
    @overrides(FlaskParameter)
    def get_dict(self) -> Dict:
        return request.headers
