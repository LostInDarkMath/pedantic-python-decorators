from abc import ABC, abstractmethod
from typing import Any, Dict

from flask import request

from pedantic.decorators.fn_deco_validate.exceptions import ValidationError, InvalidHeader
from pedantic.decorators.fn_deco_overrides import overrides
from pedantic.decorators.fn_deco_validate.parameters import ExternalParameter, Parameter


class FlaskParameter(ExternalParameter, ABC):
    @abstractmethod
    def get_dict(self) -> Dict[str, Any]:
        """ Returns the actual values as a dictionary. """

    @overrides(ExternalParameter)
    def load_value(self) -> Any:
        dict_ = self.get_dict()

        if dict_ is None:
            raise ValidationError(message=f'Data is not in JSON format.')

        if self.name in dict_ and dict_[self.name] is not None:
            return dict_[self.name]

        if self.default_value is not None:
            return self.default_value

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
    exception_type = InvalidHeader

    @overrides(FlaskParameter)
    def get_dict(self) -> Dict:
        return request.headers
