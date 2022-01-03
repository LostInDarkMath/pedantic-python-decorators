from enum import Enum, IntEnum
from unittest import TestCase

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


class TestValidatorIsEnum(TestCase):
    def test_validator_is_enum_convert_true(self) -> None:
        @validate(Parameter(name='x', validators=[IsEnum(MyEnum, convert=True)]))
        def foo(x):
            return x

        self.assertEqual(MyEnum.RED, foo('RED'))
        self.assertEqual(MyEnum.BLUE, foo('BLUE'))

        for value in ['fred', 1, 'GREEN']:
            with self.assertRaises(expected_exception=ParameterException):
                foo(value)

    def test_validator_is_enum_int_enum_convert_true(self) -> None:
        @validate(Parameter(name='x', validators=[IsEnum(MyIntEnum, convert=True)]))
        def foo(x):
            return x

        self.assertEqual(MyIntEnum.RED, foo('1'))
        self.assertEqual(MyIntEnum.BLUE, foo('2'))
        self.assertEqual(MyIntEnum.RED, foo(1))
        self.assertEqual(MyIntEnum.BLUE, foo(2))

        for value in ['fred', 3, 'GREEN']:
            with self.assertRaises(expected_exception=ParameterException):
                foo(value)

    def test_validator_is_enum_convert_false(self) -> None:
        @validate(Parameter(name='x', validators=[IsEnum(MyEnum, convert=False)]))
        def foo(x):
            return x

        self.assertEqual('RED', foo('RED'))
        self.assertEqual('BLUE', foo('BLUE'))

        for value in ['fred', 1, 'GREEN']:
            with self.assertRaises(expected_exception=ParameterException):
                foo(value)

    def test_validator_is_enum_to_upper_case(self) -> None:
        @validate(Parameter(name='x', validators=[IsEnum(MyEnum, convert=False)]))
        def foo(x):
            return x

        self.assertEqual('RED', foo('red'))
        self.assertEqual('BLUE', foo('blue'))
        self.assertEqual('BLUE', foo('bLUe'))

    def test_validator_is_enum_to_upper_case_disabled(self) -> None:
        @validate(Parameter(name='x', validators=[IsEnum(MyEnum, convert=False, to_upper_case=False)]))
        def foo(x):
            return x

        for value in ['red', 'blue', 'Red', 'bLUe']:
            with self.assertRaises(expected_exception=ParameterException):
                foo(value)
