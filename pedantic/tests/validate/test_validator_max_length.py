from unittest import TestCase

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import MaxLength


class TestValidatorMaxLength(TestCase):
    def test_validator_max_length(self) -> None:
        @validate(Parameter(name='x', validators=[MaxLength(3)]))
        def foo(x):
            return x

        self.assertEqual('hi', foo('hi'))
        self.assertEqual('hi!', foo('hi!'))
        self.assertEqual([1, 2, 3], foo([1, 2, 3]))

        with self.assertRaises(expected_exception=ParameterException):
            foo('hi!!')

        with self.assertRaises(expected_exception=ParameterException):
            foo([1, 2, 3, 4])

        with self.assertRaises(expected_exception=ParameterException):
            foo(42)
