from unittest import TestCase

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import Composite, Max, Min


class TestValidatorComposite(TestCase):
    def test_validator_composite(self) -> None:
        @validate(Parameter(name='x', validators=[Composite([Min(3), Max(5)])]))
        def foo(x):
            return x

        self.assertEqual(3, foo(3))
        self.assertEqual(4, foo(4))
        self.assertEqual(5, foo(5))

        with self.assertRaises(expected_exception=ParameterException):
            foo(5.0001)

        with self.assertRaises(expected_exception=ParameterException):
            foo(2.9999)
