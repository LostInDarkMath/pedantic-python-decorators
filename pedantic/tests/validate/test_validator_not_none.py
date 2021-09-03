from unittest import TestCase

from pedantic.decorators.fn_deco_validate.exceptions import ValidationError
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import NotNone


class TestValidatorNotEmpty(TestCase):
    def test_validator_not_none(self) -> None:
        @validate(Parameter(name='x', validators=[NotNone()]))
        def foo(x):
            return x

        self.assertEqual('hi', foo('hi'))
        self.assertEqual([1], foo([1]))

        with self.assertRaises(expected_exception=ValidationError):
            foo(None)
