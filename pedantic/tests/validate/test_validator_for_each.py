from unittest import TestCase

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import ForEach, Min, Max


class TestValidatorForEach(TestCase):
    def test_validator_for_each_single_child(self) -> None:
        @validate(Parameter(name='x', validators=[ForEach(Min(3))]))
        def foo(x):
            return x

        self.assertEqual([3, 4, 5], foo([3, 4, 5]))

        for value in [42, [3, 2, 5]]:
            with self.assertRaises(expected_exception=ParameterException):
                foo(value)

    def test_validator_for_each_multiple_children(self) -> None:
        @validate(Parameter(name='x', validators=[ForEach([Min(3), Max(4)])]))
        def foo(x):
            return x

        self.assertEqual([3, 4], foo([3, 4]))

        for value in [42, [3, 2, 5]]:
            with self.assertRaises(expected_exception=ParameterException):
                foo(value)
