import pytest

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import NotEmpty


def test_validator_not_empty():
    @validate(Parameter(name='x', validators=[NotEmpty()]))
    def foo(x):
        return x

    assert foo('hi') == 'hi'
    assert foo('   hi     ') == 'hi'
    assert foo([1]) == [1]

    for value in ['', '   ', [], {}, set()]:
        with pytest.raises(expected_exception=ParameterException):
            foo(value)
