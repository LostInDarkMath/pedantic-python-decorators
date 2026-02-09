import pytest

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import MinLength


def test_validator_min_length():
    @validate(Parameter(name='x', validators=[MinLength(3)]))
    def foo(x):
        return x

    assert foo('hi!') == 'hi!'
    assert foo('hello') == 'hello'
    assert foo([1, 2, 3]) == [1, 2, 3]

    with pytest.raises(expected_exception=ParameterException) as err:
        foo('hi')

    assert err.value.message  == 'hi is too short with length 2.'

    with pytest.raises(expected_exception=ParameterException) as err:
        foo([1, 2])

    assert err.value.message  == '[1, 2] is too short with length 2.'

    with pytest.raises(expected_exception=ParameterException) as err:
        foo(42)

    assert err.value.message  == '42 has no length.'
