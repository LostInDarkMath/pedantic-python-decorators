from abc import ABC, abstractmethod
from typing import Any

from flask import request

from pedantic.decorators.fn_deco_overrides import overrides
from pedantic.decorators.fn_deco_validate.exceptions import InvalidHeader, ParameterException, ValidatorException
from pedantic.decorators.fn_deco_validate.parameters import ExternalParameter, Parameter
from pedantic.decorators.fn_deco_validate.parameters.deserializable import Deserializable


class FlaskParameter(ExternalParameter, ABC):  # noqa: D101
    @abstractmethod
    def get_dict(self) -> dict[str, Any]:
        """Returns the actual values as a dictionary."""

    @overrides(ExternalParameter)
    def has_value(self) -> bool:  # noqa: D102
        dict_ = self.get_dict()
        return dict_ is not None and self.name in dict_

    @overrides(ExternalParameter)
    def load_value(self) -> Any:  # noqa: D102
        dict_ = self.get_dict()
        return dict_[self.name]


class FlaskJsonParameter(FlaskParameter):  # noqa: D101
    @overrides(FlaskParameter)
    def get_dict(self) -> dict:  # noqa: D102
        if not request.is_json:
            return {}

        return request.json


class FlaskFormParameter(FlaskParameter):  # noqa: D101
    @overrides(FlaskParameter)
    def get_dict(self) -> dict:  # noqa: D102
        return request.form


class FlaskPathParameter(Parameter):
    """
    This is a special case because Flask passes path parameter as kwargs to validate().
    Therefore, this doesn't need to be an ExternalParameter.
    """


class FlaskGetParameter(FlaskParameter):  # noqa: D101
    @overrides(FlaskParameter)
    def get_dict(self) -> dict:  # noqa: D102
        return request.args

    @overrides(ExternalParameter)
    def load_value(self) -> Any:  # noqa: D102
        value = request.args.getlist(self.name)

        if self.value_type is list:
            return value

        return value[0]


class FlaskHeaderParameter(FlaskParameter):  # noqa: D101
    exception_type = InvalidHeader

    @overrides(FlaskParameter)
    def get_dict(self) -> dict:  # noqa: D102
        return request.headers


class GenericFlaskDeserializer(ExternalParameter):
    """
    A JSON deserializer for classes which implements the [Deserializable] interface.

    Further reading: https://github.com/LostInDarkMath/pedantic-python-decorators/issues/55
    """

    def __init__(self, cls: type[Deserializable], catch_exception: bool = True, **kwargs: Any) -> None:  # noqa: D107
        super().__init__(**kwargs)
        self._cls = cls
        self._catch_exceptions = catch_exception

    @overrides(ExternalParameter)
    def has_value(self) -> bool:  # noqa: D102
        return request.is_json

    @overrides(ExternalParameter)
    def load_value(self) -> Any:  # noqa: D102
        try:
            return self._cls.from_json(request.json)
        except ValidatorException as ex:
            raise ParameterException.from_validator_exception(exception=ex, parameter_name='') from ex
        except Exception as ex:
            if self._catch_exceptions:
                self.raise_exception(msg=str(ex))

            raise
