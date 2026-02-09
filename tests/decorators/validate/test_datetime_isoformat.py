from datetime import datetime, timedelta

import pytest

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import DatetimeIsoFormat


def test_validator_datetime_iso_format():
    @validate(Parameter(name='x', validators=[DatetimeIsoFormat()]))
    def foo(x):
        return x

    now = datetime.now()
    assert abs(now - foo(now.isoformat()) )< timedelta(milliseconds=1)

    with pytest.raises(expected_exception=ParameterException):
        foo('12.12.2020')

    with pytest.raises(expected_exception=ParameterException):
        foo('invalid')
