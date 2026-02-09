import pytest

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import MaxLength


def test_validator_max_length():
    @validate(Parameter(name='x', validators=[MaxLength(3)]))
    def foo(x):
        return x

    assert foo('hi') == 'hi'
    assert foo('hi!') == 'hi!'
    assert foo([1, 2, 3]) == [1, 2, 3]

    with pytest.raises(expected_exception=ParameterException) as err:
        foo('hi!!')

    assert err.value.message == 'hi!! is too long with length 4.'

    with pytest.raises(expected_exception=ParameterException) as err:
        foo([1, 2, 3, 4])

    assert err.value.message  == '[1, 2, 3, 4] is too long with length 4.'

    with pytest.raises(expected_exception=ParameterException) as err:
        foo(42)

    assert err.value.message  == '42 has no length.'
