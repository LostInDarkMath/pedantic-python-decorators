from abc import ABC, abstractmethod
from typing import Any, Dict, Type

from flask import request

from pedantic.decorators.fn_deco_validate.exceptions import InvalidHeader, ParameterException, ValidatorException
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


class Deserializable(ABC):
    """ A tiny interface which has a static from_json() method which acts like a named constructor. """

    @staticmethod
    @abstractmethod
    def from_json(data: Dict[str, Any]) -> 'Deserializable':
        """ A named constructor which creates an object from JSON. """


class GenericFlaskDeserializer(ExternalParameter):
    """
        A JSON deserializer for classes which implements the [Deserializable] interface.

        Further reading: https://github.com/LostInDarkMath/pedantic-python-decorators/issues/55
    """

    def __init__(self, cls: Type[Deserializable], catch_exception: bool = True, **kwargs) -> None:
        super().__init__(**kwargs)
        self._cls = cls
        self._catch_exceptions = catch_exception

    @overrides(ExternalParameter)
    def has_value(self) -> bool:
        return request.is_json

    @overrides(ExternalParameter)
    def load_value(self) -> Any:
        try:
            return self._cls.from_json(request.json)
        except ValidatorException as ex:
            raise ParameterException.from_validator_exception(exception=ex, parameter_name='')
        except Exception as ex:
            if self._catch_exceptions:
                self.raise_exception(msg=str(ex))

            raise ex
