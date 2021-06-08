from typing import Any

from flask import request

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.parameters import ExternalParameter


class FlaskJsonParameter(ExternalParameter):
    @overrides(ExternalParameter)
    def load_value(self) -> Any:
        return request.json[self.name]


class FlaskFormParameter(ExternalParameter):
    @overrides(ExternalParameter)
    def load_value(self) -> Any:
        return request.data[self.name]


class FlaskPathParameter(ExternalParameter):
    @overrides(ExternalParameter)
    def load_value(self) -> Any:
        return request.path[self.name]
