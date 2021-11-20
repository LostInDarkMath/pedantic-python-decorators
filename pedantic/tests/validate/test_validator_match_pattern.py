from unittest import TestCase

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import MatchPattern


class TestValidatorMatchPattern(TestCase):
    def test_validator_match_pattern(self) -> None:
        pattern = r'^(([01]\d|2[0-3]):([0-5]\d)|24:00)$'

        @validate(Parameter(name='x', validators=[MatchPattern(pattern)]))
        def foo(x):
            return x

        for value in ['00:00', '02:45', '14:59', '23:59']:
            self.assertEqual(value, foo(value))

        for value in ['00:70', '24:00', '30:00', 'invalid']:
            with self.assertRaises(expected_exception=ParameterException):
                foo([3, 2, 5])
