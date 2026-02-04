from unittest import TestCase

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import MinLength


class TestValidatorMinLength(TestCase):
    def test_validator_min_length(self) -> None:
        @validate(Parameter(name='x', validators=[MinLength(3)]))
        def foo(x):
            return x

        self.assertEqual('hi!', foo('hi!'))
        self.assertEqual('hello', foo('hello'))
        self.assertEqual([1, 2, 3], foo([1, 2, 3]))

        with self.assertRaises(expected_exception=ParameterException) as ex:
            foo('hi')

        assert ex.exception.message == 'hi is too short with length 2.'

        with self.assertRaises(expected_exception=ParameterException) as ex:
            foo([1, 2])

        assert ex.exception.message == '[1, 2] is too short with length 2.'

        with self.assertRaises(expected_exception=ParameterException) as ex:
            foo(42)

        assert ex.exception.message == '42 has no length.'
