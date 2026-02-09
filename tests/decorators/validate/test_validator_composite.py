import pytest

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import Composite, Max, Min


def test_validator_composite():
    @validate(Parameter(name='x', validators=[Composite([Min(3), Max(5)])]))
    def foo(x):
        return x

    assert foo(3) == 3
    assert foo(4) == 4
    assert foo(5) == 5

    with pytest.raises(expected_exception=ParameterException):
        foo(5.0001)

    with pytest.raises(expected_exception=ParameterException):
        foo(2.9999)
