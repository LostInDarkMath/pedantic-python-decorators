import pytest

from pedantic import MaxLength, Parameter, ParameterException, validate


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
