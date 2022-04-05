from datetime import datetime, timedelta
from unittest import TestCase

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import DatetimeIsoFormat


class TestValidatorDatetimeIsoformat(TestCase):
    def test_validator_datetime_isoformat(self) -> None:
        @validate(Parameter(name='x', validators=[DatetimeIsoFormat()]))
        def foo(x):
            return x

        now = datetime.now()
        self.assertTrue(abs((now - foo(now.isoformat()) < timedelta(milliseconds=1))))

        with self.assertRaises(expected_exception=ParameterException):
            foo('12.12.2020')

        with self.assertRaises(expected_exception=ParameterException):
            foo('invalid')
