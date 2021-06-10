import os
from unittest import TestCase

from pedantic.decorators.fn_deco_validate.exceptions import ValidationError
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter, EnvironmentVariableParameter
from pedantic.decorators.fn_deco_validate.validators import MaxLength, Min, Max


class TestValidate(TestCase):
    def setUp(self) -> None:
        if 'foo' in os.environ:
            del os.environ['foo']

    def test_single_validator(self) -> None:
        validator = MaxLength(3)
        converted_value = validator.validate(value='hed')
        self.assertEqual(converted_value, 'hed')

        with self.assertRaises(expected_exception=ValidationError):
            validator.validate(value='hello world')

    def test_single_parameter(self) -> None:
        parameter = Parameter(name='x', validators=[MaxLength(3)])
        converted_value = parameter.validate(value='hed')
        self.assertEqual(converted_value, 'hed')

        with self.assertRaises(expected_exception=ValidationError):
            parameter.validate(value='hello world')

    def test_multiple_parameters(self) -> None:
        @validate(
            Parameter(name='a', validators=[Min(3)]),
            Parameter(name='b', validators=[Max(3)]),
            Parameter(name='c', validators=[Max(43)]),
        )
        def bar(a, b, c):
            return a + b + c

        self.assertEqual(11, bar(3, 3, 5))
        self.assertEqual(11, bar(a=3, b=3, c=5))

    def test_external_parameter_accepts_value_when_given(self) -> None:
        @validate(EnvironmentVariableParameter(name='foo'))
        def bar(foo):
            return foo

        self.assertEqual('42', bar('42'))
        self.assertEqual('42', bar(foo='42'))

    def test_external_parameter_mixed_with_normal_parameter(self) -> None:
        @validate(
            EnvironmentVariableParameter(name='foo'),
            Parameter(name='footer'),
        )
        def bar(foo, footer):
            return foo, footer

        self.assertEqual(('42', 3), bar('42', 3))

        os.environ['foo'] = '42'
        self.assertEqual(('42', 3), bar(footer=3))


