from unittest import TestCase

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import NotEmpty


class TestValidatorNotEmpty(TestCase):
    def test_validator_not_empty(self) -> None:
        @validate(Parameter(name='x', validators=[NotEmpty()]))
        def foo(x):
            return x

        self.assertEqual('hi', foo('hi'))
        self.assertEqual('hi', foo('   hi     '))
        self.assertEqual([1], foo([1]))

        for value in ['', '   ', [], {}, set()]:
            with self.assertRaises(expected_exception=ParameterException):
                foo(value)
