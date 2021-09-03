from enum import Enum
from unittest import TestCase

from pedantic.decorators.fn_deco_validate.exceptions import ValidationError
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import IsEnum


class MyEnum(Enum):
    RED = 'RED'
    BLUE = 'BLUE'


class TestValidatorIsEnum(TestCase):
    def test_validator_is_enum_convert_true(self) -> None:
        @validate(Parameter(name='x', validators=[IsEnum(MyEnum, convert=True)]))
        def foo(x):
            return x

        self.assertEqual(MyEnum.RED, foo('RED'))
        self.assertEqual(MyEnum.BLUE, foo('BLUE'))

        for value in ['fred', 1, 'GREEN']:
            with self.assertRaises(expected_exception=ValidationError):
                foo(value)

    def test_validator_is_enum_convert_false(self) -> None:
        @validate(Parameter(name='x', validators=[IsEnum(MyEnum, convert=False)]))
        def foo(x):
            return x

        self.assertEqual('RED', foo('RED'))
        self.assertEqual('BLUE', foo('BLUE'))

        for value in ['fred', 1, 'GREEN']:
            with self.assertRaises(expected_exception=ValidationError):
                foo(value)
