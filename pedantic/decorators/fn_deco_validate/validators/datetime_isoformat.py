from datetime import datetime

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.validators import Validator


class DatetimeIsoFormat(Validator):
    @overrides(Validator)
    def validate(self, value: str) -> datetime:
        try:
            value = datetime.fromisoformat(value)
        except (TypeError, ValueError, AttributeError):
            self.raise_exception(msg=f'invalid value: {value} is not a datetime in ISO format', value=value)

        return value
