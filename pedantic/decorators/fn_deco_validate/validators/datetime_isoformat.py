import sys
from datetime import datetime

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.validators import Validator


class DatetimeIsoFormat(Validator):
    @overrides(Validator)
    def validate(self, value: str) -> datetime:
        try:
            if sys.version_info >= (3, 7):
                value = datetime.fromisoformat(value)
            else:
                value = datetime_from_iso_format(value)
        except (TypeError, ValueError, AttributeError):
            self.raise_exception(msg=f'invalid value: {value} is not a datetime in ISO format', value=value)

        return value


def datetime_from_iso_format(value: str) -> datetime:
    """
        For python versions < 3.7: Get datetime from iso format.
        Source: https://github.com/fitoprincipe/ipygee/blob/master/ipygee/tasks.py#L80
    """

    d, t = value.split('T')
    year, month, day = d.split('-')
    hours, minutes, seconds = t.split(':')
    seconds = float(seconds[0:-1])
    sec = int(seconds)
    microseconds = int((seconds-sec)*1e6)

    return datetime(int(year), int(month), int(day), int(hours), int(minutes), sec, microseconds)
