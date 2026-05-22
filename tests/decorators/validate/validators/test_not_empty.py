import pytest

from pedantic import NotEmpty, Parameter, ParameterException, validate


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
