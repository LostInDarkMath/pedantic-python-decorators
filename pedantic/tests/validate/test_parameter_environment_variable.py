import os
from unittest import TestCase

from pedantic.decorators.fn_deco_validate.exceptions import ValidationError
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import EnvironmentVariableParameter


class TestParameterEnvironmentVariable(TestCase):
    def setUp(self) -> None:
        if 'foo' in os.environ:
            del os.environ['foo']

    def test_parameter_environment_variable_str(self) -> None:
        @validate(EnvironmentVariableParameter(name='foo', value_type=str))
        def bar(foo):
            return foo

        os.environ['foo'] = '42'
        self.assertEqual('42', bar())

    def test_parameter_environment_variable_int(self) -> None:
        @validate(EnvironmentVariableParameter(name='foo', value_type=int))
        def bar(foo):
            return foo

        os.environ['foo'] = '42'
        self.assertEqual(42, bar())

    def test_parameter_environment_variable_float(self) -> None:
        @validate(EnvironmentVariableParameter(name='foo', value_type=float))
        def bar(foo):
            return foo

        os.environ['foo'] = '42.7'
        self.assertEqual(42.7, bar())

    def test_parameter_environment_variable_bool(self) -> None:
        @validate(EnvironmentVariableParameter(name='foo', value_type=bool))
        def bar(foo):
            return foo

        for value in ['true', 'True', 'TRUE']:
            os.environ['foo'] = value
            self.assertTrue(bar())

        for value in ['false', 'False', 'FALSE']:
            os.environ['foo'] = value
            self.assertFalse(bar())

        for value in ['invalid', 'frue', 'talse']:
            os.environ['foo'] = value

            with self.assertRaises(expected_exception=ValidationError):
                bar()

    def test_parameter_environment_variable_not_set(self) -> None:
        @validate(EnvironmentVariableParameter(name='foo'))
        def bar(foo):
            return foo

        with self.assertRaises(expected_exception=ValidationError):
            bar()
