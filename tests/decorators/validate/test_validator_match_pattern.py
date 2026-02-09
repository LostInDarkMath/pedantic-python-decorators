import pytest

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import MatchPattern


def test_validator_match_pattern():
    pattern = r'^(([01]\d|2[0-3]):([0-5]\d)|24:00)$'

    @validate(Parameter(name='x', validators=[MatchPattern(pattern)]))
    def foo(x):
        return x

    for value in ['00:00', '02:45', '14:59', '23:59', '24:00']:
        assert foo(value) == value

    for value in ['00:70', '24:01', '30:00', 'invalid']:
        with pytest.raises(expected_exception=ParameterException):
            foo(value)
