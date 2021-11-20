from datetime import datetime
from unittest import TestCase

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import DateTimeUnixTimestamp


class TestValidatorDatetimeUnixTimestamp(TestCase):
    def test_validator_datetime_unix_timestamp(self) -> None:
        @validate(Parameter(name='x', validators=[DateTimeUnixTimestamp()]))
        def foo(x):
            return x

        now = datetime.now()
        unix_timestamp = (now - datetime(year=1970, month=1, day=1)).total_seconds()
        self.assertEqual(now, foo(unix_timestamp))
        self.assertEqual(now, foo(str(unix_timestamp)))

        with self.assertRaises(expected_exception=ParameterException):
            foo('12.12.2020')

        with self.assertRaises(expected_exception=ParameterException):
            foo('invalid')

        with self.assertRaises(expected_exception=ParameterException):
            foo({'a': 1})
