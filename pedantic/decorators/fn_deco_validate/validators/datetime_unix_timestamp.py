from datetime import UTC, datetime, timedelta

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.validators import Validator


class DateTimeUnixTimestamp(Validator): # noqa: D101
    @overrides(Validator)
    def validate(self, value: float | str) -> datetime: # noqa: D102
        if not isinstance(value, (int, float, str)):
            self.raise_exception(msg=f'Invalid seconds since 1970: {value}', value=value)

        try:
            seconds = float(value)
        except ValueError:
            return self.raise_exception(msg=f'Could parse {value} to float.', value=value)

        try:
            return datetime(year=1970, month=1, day=1, tzinfo=UTC) + timedelta(seconds=seconds)
        except OverflowError:
            return self.raise_exception(
                msg=f'Date value out of range. Make sure you send SECONDS since 1970. Got: {value}', value=value)
