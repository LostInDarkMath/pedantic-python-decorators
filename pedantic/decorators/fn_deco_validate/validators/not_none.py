from typing import Any

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.exceptions import ValidationError
from pedantic.decorators.fn_deco_validate.validators import Validator


class NotNone(Validator):
    @overrides(Validator)
    def validate(self, value: Any) -> Any:
        if value is None:
            raise ValidationError(f'Got None value')

        return value
