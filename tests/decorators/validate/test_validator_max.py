import pytest

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators.max import Max


def test_validator_max_length_include_boundary_true():
    @validate(Parameter(name='x', validators=[Max(3, include_boundary=True)]))
    def foo(x):
        return x

    assert foo(3) == 3
    assert foo(2) == 2

    with pytest.raises(expected_exception=ParameterException):
        foo(4)

    with pytest.raises(expected_exception=ParameterException):
        foo(3.001)

def test_validator_max_length_include_boundary_false():
    @validate(Parameter(name='x', validators=[Max(3, include_boundary=False)]))
    def foo(x):
        return x

    assert foo(2.9999) == 2.9999
    assert foo(2) == 2

    with pytest.raises(expected_exception=ParameterException):
        foo(4)

    with pytest.raises(expected_exception=ParameterException):
        foo(3)
