from abc import ABC, abstractmethod
from typing import Any, Dict

from flask import request

from pedantic.decorators.fn_deco_validate.exceptions import InvalidHeader
from pedantic.decorators.fn_deco_overrides import overrides
from pedantic.decorators.fn_deco_validate.parameters import ExternalParameter, Parameter


class FlaskParameter(ExternalParameter, ABC):
    @abstractmethod
    def get_dict(self) -> Dict[str, Any]:
        """ Returns the actual values as a dictionary. """

    @overrides(ExternalParameter)
    def has_value(self) -> bool:
        dict_ = self.get_dict()
        return dict_ is not None and self.name in dict_

    @overrides(ExternalParameter)
    def load_value(self) -> Any:
        dict_ = self.get_dict()
        return dict_[self.name]


class FlaskJsonParameter(FlaskParameter):
    @overrides(FlaskParameter)
    def get_dict(self) -> Dict:
        if not request.is_json:
            return {}

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

    @overrides(ExternalParameter)
    def load_value(self) -> Any:
        value = request.args.getlist(self.name)

        if self.value_type == list:
            return value

        return value[0]


class FlaskHeaderParameter(FlaskParameter):
    exception_type = InvalidHeader

    @overrides(FlaskParameter)
    def get_dict(self) -> Dict:
        return request.headers
