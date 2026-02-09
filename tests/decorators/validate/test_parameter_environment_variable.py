import os

import pytest

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import EnvironmentVariableParameter


def test_parameter_environment_variable_str():
    @validate(EnvironmentVariableParameter(name='foo', value_type=str))
    def bar(foo):
        return foo

    os.environ['foo'] = '42'
    assert bar() == '42'


def test_parameter_environment_variable_int():
    @validate(EnvironmentVariableParameter(name='foo', value_type=int))
    def bar(foo):
        return foo

    os.environ['foo'] = '42'
    assert bar() == 42


def test_parameter_environment_variable_float():
    @validate(EnvironmentVariableParameter(name='foo', value_type=float))
    def bar(foo):
        return foo

    os.environ['foo'] = '42.7'
    assert bar() == 42.7


def test_parameter_environment_variable_bool():
    @validate(EnvironmentVariableParameter(name='foo', value_type=bool))
    def bar(foo):
        return foo

    for value in ['true', 'True', 'TRUE']:
        os.environ['foo'] = value
        assert bar() is True

    for value in ['false', 'False', 'FALSE']:
        os.environ['foo'] = value
        assert bar() is False

    for value in ['invalid', 'frue', 'talse']:
        os.environ['foo'] = value

        with pytest.raises(expected_exception=ParameterException):
            bar()

def test_parameter_environment_variable_not_set():
    @validate(EnvironmentVariableParameter(name='foo'))
    def bar(foo):
        return foo

    with pytest.raises(expected_exception=ParameterException):
        bar()


def test_invalid_value_type():
    with pytest.raises(expected_exception=AssertionError):
        @validate(EnvironmentVariableParameter(name='foo', value_type=dict))
        def bar(foo):
            return foo


def test_parameter_environment_variable_different_name():
    @validate(EnvironmentVariableParameter(name='foo', env_var_name='fuu', value_type=str))
    def bar(foo):
        return foo

    os.environ['fuu'] = '42'
    assert bar() == '42'


def test_two_parameters():
    @validate(EnvironmentVariableParameter(name='a'), strict=False)
    def foo(a: float, b: int) -> str:
        return f'{a} and {b}'

    os.environ['a'] = '42'
    assert foo(b=42) == '42 and 42'
