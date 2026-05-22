import pytest

from pedantic import ForEach, Max, Min, Parameter, ParameterException, validate


def test_validator_for_each_single_child():
    @validate(Parameter(name='x', validators=[ForEach(Min(3))]))
    def foo(x):
        return x

    assert foo([3, 4, 5]) == [3, 4, 5]

    for value in [42, [3, 2, 5]]:
        with pytest.raises(expected_exception=ParameterException):
            foo(value)


def test_validator_for_each_multiple_children():
    @validate(Parameter(name='x', validators=[ForEach([Min(3), Max(4)])]))
    def foo(x):
        return x

    assert foo([3, 4]) == [3, 4]

    for value in [42, [3, 2, 5]]:
        with pytest.raises(expected_exception=ParameterException):
            foo(value)
