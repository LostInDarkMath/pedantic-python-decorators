from datetime import UTC, datetime, timedelta

import pytest

from pedantic import DatetimeIsoFormat, Parameter, ParameterException, validate


def test_validator_datetime_iso_format():
    @validate(Parameter(name='x', validators=[DatetimeIsoFormat()]))
    def foo(x):
        return x

    now = datetime.now(tz=UTC)
    assert abs(now - foo(now.isoformat()) )< timedelta(milliseconds=1)

    with pytest.raises(expected_exception=ParameterException):
        foo('12.12.2020')

    with pytest.raises(expected_exception=ParameterException):
        foo('invalid')
