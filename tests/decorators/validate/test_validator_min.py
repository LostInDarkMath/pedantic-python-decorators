import pytest

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import Min


def test_validator_min_length_include_boundary_true():
    @validate(Parameter(name='x', validators=[Min(3, include_boundary=True)]))
    def foo(x):
        return x

    assert foo(3) == 3
    assert foo(4) == 4

    with pytest.raises(expected_exception=ParameterException):
        foo(2)

    with pytest.raises(expected_exception=ParameterException):
        foo(2.9999)


def test_validator_min_length_include_boundary_false():
    @validate(Parameter(name='x', validators=[Min(3, include_boundary=False)]))
    def foo(x):
        return x

    assert foo(3.0001) == 3.0001
    assert foo(4) == 4

    with pytest.raises(expected_exception=ParameterException):
        foo(2)

    with pytest.raises(expected_exception=ParameterException):
        foo(3)
