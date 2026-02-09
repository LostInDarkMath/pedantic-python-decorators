from datetime import datetime

import pytest

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import DateTimeUnixTimestamp


def test_validator_datetime_unix_timestamp():
    @validate(Parameter(name='x', validators=[DateTimeUnixTimestamp()]))
    def foo(x):
        return x

    now = datetime.now()
    unix_timestamp = (now - datetime(year=1970, month=1, day=1)).total_seconds()
    assert foo(unix_timestamp) == now
    assert foo(str(unix_timestamp)) == now

    with pytest.raises(expected_exception=ParameterException):
        foo('12.12.2020')

    with pytest.raises(expected_exception=ParameterException):
        foo('invalid')

    with pytest.raises(expected_exception=ParameterException):
        foo({'a': 1})

    with pytest.raises(expected_exception=ParameterException):
        foo(unix_timestamp * 1000)
