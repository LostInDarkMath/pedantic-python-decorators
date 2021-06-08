import os
from typing import Any

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.parameters import ExternalParameter


class EnvironmentVariableParameter(ExternalParameter):
    @overrides(ExternalParameter)
    def load_value(self) -> Any:
        return os.environ[self.name]
