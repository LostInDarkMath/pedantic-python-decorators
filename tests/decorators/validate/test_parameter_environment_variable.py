import os

import pytest

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import EnvironmentVariableParameter


def test_parameter_environment_variable_str():
    @validate(EnvironmentVariableParameter(name='FOO', value_type=str))
    def bar(foo):
        return foo

    os.environ['FOO'] = '42'
    assert bar() == '42'


def test_parameter_environment_variable_int():
    @validate(EnvironmentVariableParameter(name='FOO', value_type=int))
    def bar(foo):
        return foo

    os.environ['FOO'] = '42'
    assert bar() == 42


def test_parameter_environment_variable_float():
    @validate(EnvironmentVariableParameter(name='FOO', value_type=float))
    def bar(foo):
        return foo

    os.environ['FOO'] = '42.7'
    assert bar() == 42.7


def test_parameter_environment_variable_bool():
    @validate(EnvironmentVariableParameter(name='FOO', value_type=bool))
    def bar(foo):
        return foo

    for value in ['true', 'True', 'TRUE']:
        os.environ['FOO'] = value
        assert bar() is True

    for value in ['false', 'False', 'FALSE']:
        os.environ['FOO'] = value
        assert bar() is False

    for value in ['invalid', 'frue', 'talse']:
        os.environ['FOO'] = value

        with pytest.raises(expected_exception=ParameterException):
            bar()

def test_parameter_environment_variable_not_set():
    @validate(EnvironmentVariableParameter(name='FOO'))
    def bar(foo):
        return foo

    with pytest.raises(expected_exception=ParameterException):
        bar()


def test_invalid_value_type():
    with pytest.raises(expected_exception=AssertionError):
        @validate(EnvironmentVariableParameter(name='FOO', value_type=dict))
        def bar(foo):
            return foo


def test_parameter_environment_variable_different_name():
    @validate(EnvironmentVariableParameter(name='FOO', env_var_name='fuu', value_type=str))
    def bar(foo):
        return foo

    os.environ['FUU'] = '42'
    assert bar() == '42'


def test_two_parameters():
    @validate(EnvironmentVariableParameter(name='A'), strict=False)
    def foo(a: float, b: int) -> str:
        return f'{a} and {b}'

    os.environ['A'] = '42'
    assert foo(b=42) == '42 and 42'
