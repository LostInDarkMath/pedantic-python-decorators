from enum import Enum, IntEnum

import pytest

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import IsEnum


class MyEnum(Enum):
    RED = 'RED'
    BLUE = 'BLUE'


class MyIntEnum(IntEnum):
    RED = 1
    BLUE = 2


def test_validator_is_enum_convert_true():
    @validate(Parameter(name='x', validators=[IsEnum(MyEnum, convert=True)]))
    def foo(x):
        return x

    assert foo('RED') == MyEnum.RED
    assert foo('BLUE') == MyEnum.BLUE

    for value in ['fred', 1, 'GREEN']:
        with pytest.raises(expected_exception=ParameterException):
            foo(value)


def test_validator_is_enum_int_enum_convert_true():
    @validate(Parameter(name='x', validators=[IsEnum(MyIntEnum, convert=True)]))
    def foo(x):
        return x

    assert foo('1') == MyIntEnum.RED
    assert foo('2') == MyIntEnum.BLUE
    assert foo(1) == MyIntEnum.RED
    assert foo(2) == MyIntEnum.BLUE

    for value in ['fred', 3, 'GREEN']:
        with pytest.raises(expected_exception=ParameterException):
            foo(value)


def test_validator_is_enum_convert_false():
    @validate(Parameter(name='x', validators=[IsEnum(MyEnum, convert=False)]))
    def foo(x):
        return x

    assert foo('RED') == 'RED'
    assert foo('BLUE') == 'BLUE'

    for value in ['fred', 1, 'GREEN']:
        with pytest.raises(expected_exception=ParameterException):
            foo(value)


def test_validator_is_enum_to_upper_case():
    @validate(Parameter(name='x', validators=[IsEnum(MyEnum, convert=False)]))
    def foo(x):
        return x

    assert foo('red') == 'RED'
    assert foo('blue') == 'BLUE'
    assert foo('bLUe') == 'BLUE'


def test_validator_is_enum_to_upper_case_disabled():
    @validate(Parameter(name='x', validators=[IsEnum(MyEnum, convert=False, to_upper_case=False)]))
    def foo(x): print(x)

    for value in ['red', 'blue', 'Red', 'bLUe']:
        with pytest.raises(expected_exception=ParameterException):
            foo(value)
