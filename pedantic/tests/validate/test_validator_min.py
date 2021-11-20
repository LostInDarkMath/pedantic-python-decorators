from unittest import TestCase

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import Min


class TestValidatorMin(TestCase):
    def test_validator_min_length_include_boundary_true(self) -> None:
        @validate(Parameter(name='x', validators=[Min(3, include_boundary=True)]))
        def foo(x):
            return x

        self.assertEqual(3, foo(3))
        self.assertEqual(4, foo(4))

        with self.assertRaises(expected_exception=ParameterException):
            foo(2)

        with self.assertRaises(expected_exception=ParameterException):
            foo(2.9999)

    def test_validator_min_length_include_boundary_false(self) -> None:
        @validate(Parameter(name='x', validators=[Min(3, include_boundary=False)]))
        def foo(x):
            return x

        self.assertEqual(3.0001, foo(3.0001))
        self.assertEqual(4, foo(4))

        with self.assertRaises(expected_exception=ParameterException):
            foo(2)

        with self.assertRaises(expected_exception=ParameterException):
            foo(3)
