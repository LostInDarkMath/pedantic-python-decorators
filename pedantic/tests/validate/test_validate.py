import os
import sys
from datetime import datetime
from typing import Optional, Any
from unittest import TestCase

if sys.version_info >= (3, 8):
    from unittest import IsolatedAsyncioTestCase  # exists since Python 3.8

from pedantic import DateTimeUnixTimestamp
from pedantic.decorators.fn_deco_validate.exceptions import ValidateException, ParameterException, \
    ValidatorException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate, ReturnAs
from pedantic.decorators.fn_deco_validate.parameters import Parameter, EnvironmentVariableParameter
from pedantic.decorators.fn_deco_validate.validators import MaxLength, Min, Max, Email, Validator


class TestValidate(TestCase):
    def setUp(self) -> None:
        if 'foo' in os.environ:
            del os.environ['foo']

    def test_single_validator(self) -> None:
        validator = MaxLength(3)
        converted_value = validator.validate(value='hed')
        self.assertEqual(converted_value, 'hed')

        with self.assertRaises(expected_exception=ValidatorException) as ex:
            validator.validate(value='hello world')

        expected_error_msg = 'MaxLength: hello world is too long with length 11. Value: hello world '
        self.assertEqual(expected_error_msg, str(ex.exception))

    def test_single_parameter(self) -> None:
        parameter = Parameter(name='x', validators=[MaxLength(3)])
        converted_value = parameter.validate(value='hed')
        self.assertEqual(converted_value, 'hed')

        with self.assertRaises(expected_exception=ParameterException):
            parameter.validate(value='hello world')

    def test_multiple_parameters(self) -> None:
        @validate(
            Parameter(name='a', validators=[Min(3)]),
            Parameter(name='b', validators=[Max(3)]),
            Parameter(name='c', validators=[Max(43)]),
        )
        def bar(a, b, c):
            return a + b + c

        self.assertEqual(11, bar(3, 3, 5))
        self.assertEqual(11, bar(a=3, b=3, c=5))

    def test_validate_args(self):
        @validate(
            Parameter(name='a', validators=[Min(42, include_boundary=False)]),
            Parameter(name='b', validators=[Min(42, include_boundary=False)]),
            Parameter(name='c', validators=[Min(42, include_boundary=False)]),
        )
        def some_calculation(a, b, c):
            return a + b + c

        some_calculation(43, 45, 50)
        with self.assertRaises(expected_exception=ParameterException):
            some_calculation(30, 40, 50)
        with self.assertRaises(expected_exception=ParameterException):
            some_calculation(c=30, a=40, b=50)

    def test_validate_instance_method(self):
        class MyClass:
            @validate(
                Parameter(name='x', validators=[Min(1)]),
            )
            def some_calculation(self, x: int) -> int:
                return x

        m = MyClass()
        m.some_calculation(1)
        m.some_calculation(42)

        with self.assertRaises(expected_exception=ParameterException):
            m.some_calculation(0)
        with self.assertRaises(expected_exception=ParameterException):
            m.some_calculation(-42)

    def test_validate_static_method(self):
        """ The @staticmethod decorator have to be ABOVE the @validate decorator. """

        class MyClass:
            @staticmethod
            @validate(
                Parameter(name='x', validators=[Min(1)]),
            )
            def some_calculation(x: int) -> int:
                return x

        m = MyClass()
        m.some_calculation(1)
        m.some_calculation(42)

        with self.assertRaises(expected_exception=ParameterException):
            m.some_calculation(0)
        with self.assertRaises(expected_exception=ParameterException):
            m.some_calculation(-42)

    def test_less_parameter_than_arguments(self):
        @validate(
            Parameter(name='b'),
            strict=False,
        )
        def some_calculation(a, b, c):
            return a + b + c

        some_calculation(43, 0, -50)

        with self.assertRaises(expected_exception=ValidateException):
            some_calculation(30, None, 50)

    def test_empty_parameter_kwargs_with_none(self):
        @validate(
            Parameter(name='a', required=False),
            Parameter(name='b', required=True),
            Parameter(name='c', required=False),
            return_as=ReturnAs.KWARGS_WITH_NONE
        )
        def some_calculation(a, b, c):
            return str(a) + str(b) + str(c)

        self.assertEqual('430-50', some_calculation(43, 0, -50))
        self.assertEqual('None0None', some_calculation(None, 0, None))

    def test_empty_parameter_kwargs_without_none(self):
        @validate(
            Parameter(name='a', required=False),
            Parameter(name='b', required=True),
            Parameter(name='c', required=False),
            return_as=ReturnAs.KWARGS_WITHOUT_NONE
        )
        def some_calculation(a: Optional[int] = 1, b: Optional[int] = 2, c:  Optional[int] = 3):
            return str(a) + str(b) + str(c)

        self.assertEqual('430-50', some_calculation(43, 0, -50))
        self.assertEqual('103', some_calculation(None, 0, None))

    def test_required(self):
        @validate(
            Parameter(name='a', required=True),
            Parameter(name='b', required=True),
            Parameter(name='c', required=True),
        )
        def some_calculation(a, b, c):
            return a + b + c

        some_calculation(43, 0, -50)

        with self.assertRaises(expected_exception=ValidateException):
            some_calculation(30, None, 50)

    def test_call_with_args(self):
        @validate(
            Parameter(name='x', validators=[Min(1)]),
        )
        def some_calculation(x: int) -> int:
            return x

        some_calculation(42)

    def test_external_parameter_accepts_value_when_given(self) -> None:
        @validate(EnvironmentVariableParameter(name='foo'))
        def bar(foo):
            return foo

        self.assertEqual('42', bar('42'))
        self.assertEqual('42', bar(foo='42'))

    def test_external_parameter_ignores_value_when_given(self) -> None:
        @validate(EnvironmentVariableParameter(name='foo'), ignore_input=True)
        def bar(foo):
            return foo

        os.environ['foo'] = '1'

        self.assertEqual('1', bar('42'))
        self.assertEqual('1', bar(foo='42'))

    def test_external_parameter_mixed_with_normal_parameter(self) -> None:
        @validate(
            EnvironmentVariableParameter(name='foo'),
            Parameter(name='footer'),
        )
        def bar(foo, footer):
            return foo, footer

        self.assertEqual(('42', 3), bar('42', 3))

        os.environ['foo'] = '42'
        self.assertEqual(('42', 3), bar(footer=3))

    def test_too_many_arguments(self) -> None:
        @validate(
            Parameter(name='x'),
        )
        def bar(x):
            return x

        self.assertEqual(42, bar(42))

        with self.assertRaises(expected_exception=ValidateException):
            bar(42, 43)

    def test_unexpected_parameter_strict(self) -> None:
        @validate(Parameter(name='y'))
        def bar(x):
            return x

        with self.assertRaises(expected_exception=ValidateException):
            bar(42)
        with self.assertRaises(expected_exception=ValidateException):
            bar(x=42)

    def test_unexpected_parameter_not_strict(self) -> None:
        @validate(Parameter(name='y'), strict=False)
        def bar(x):
            return x

        with self.assertRaises(expected_exception=ValidateException):
            self.assertEqual(42, bar(42))

        with self.assertRaises(expected_exception=ValidateException):
            self.assertEqual(42, bar(x=42))

    def test_unexpected_parameter_not_strict_external(self) -> None:
        @validate(EnvironmentVariableParameter(name='foo'))
        def bar(x):
            return x

        with self.assertRaises(expected_exception=ValidateException):
            self.assertEqual(42, bar(42))

        with self.assertRaises(expected_exception=ValidateException):
            self.assertEqual(42, bar(x=42))

    def test_return_as_simple(self) -> None:
        @validate(Parameter(name='x'), return_as=ReturnAs.ARGS)
        def bar(x):
            return x

        self.assertEqual(42, bar(42))
        self.assertEqual(42, bar(x=42))

    def test_return_as_args(self) -> None:
        @validate(Parameter(name='x'), return_as=ReturnAs.ARGS)
        def bar(*args, **kwargs):
            return args, kwargs

        self.assertEqual(((42,), {}), bar(42))
        self.assertEqual(((42,), {}), bar(x=42))

    def test_return_as_kwargs_with_none(self) -> None:
        @validate(Parameter(name='x'), return_as=ReturnAs.KWARGS_WITH_NONE)
        def bar(*args, **kwargs):
            return args, kwargs

        self.assertEqual(((), {'x': 42}), bar(42))
        self.assertEqual(((), {'x': 42}), bar(x=42))

    def test_return_as_kwargs_without_none(self) -> None:
        @validate(Parameter(name='x'), return_as=ReturnAs.KWARGS_WITHOUT_NONE)
        def bar(*args, **kwargs):
            return args, kwargs

        self.assertEqual(((), {'x': 42}), bar(42))
        self.assertEqual(((), {'x': 42}), bar(x=42))

    def test_return_as_args_advanced(self) -> None:
        @validate(
            Parameter(name='a'),
            Parameter(name='b'),
            Parameter(name='c'),
            return_as=ReturnAs.ARGS,
        )
        def bar(a, b, *args, **kwargs):
            return a, b, args, kwargs

        bar(a=1, b=3, c=42)
        bar(1, 3, 4)
        bar(1, 3, c=4)

    def test_return_as_args_advanced_different_order(self) -> None:
        @validate(
            Parameter(name='c'),
            Parameter(name='a'),
            Parameter(name='b'),
            return_as=ReturnAs.ARGS,
        )
        def bar(a, b, *args, **kwargs):
            return a, b, args, kwargs

        self.assertEqual((1, 3, (42,), {}), bar(a=1, b=3, c=42))
        self.assertEqual((1, 3, (42,), {}), bar(1, 3, 42))
        self.assertEqual((42, 1, (3,), {}), bar(1, 3, c=42))

    def test_return_multiple_args(self) -> None:
        @validate(
            Parameter(name='c'),
            Parameter(name='a'),
            Parameter(name='b'),
        )
        def bar(*args, **kwargs):
            return args, kwargs

        self.assertEqual(((), {'a': 1, 'b': 3, 'c': 42}), bar(a=1, b=3, c=42))
        self.assertEqual(((), {'a': 3, 'b': 42, 'c': 1}), bar(1, 3, 42))
        self.assertEqual(((), {'a': 1, 'b': 3, 'c': 42}), bar(1, 3, c=42))

    def test_none_is_not_validated_if_not_required_kwargs_with_none(self) -> None:
        @validate(Parameter(name='a', validators=[Email()], required=False), return_as=ReturnAs.KWARGS_WITH_NONE)
        def bar(a: Optional[str]):
            return a

        self.assertIsNone(bar(a=None))
        self.assertIsNone(bar(None))

        with self.assertRaises(expected_exception=ParameterException):
            bar('no_email')

    def test_none_is_not_validated_if_not_required_kwargs_without_none(self) -> None:
        @validate(Parameter(name='a', validators=[Email()], required=False), return_as=ReturnAs.KWARGS_WITHOUT_NONE)
        def bar(a: Optional[str] = None):
            return a

        self.assertIsNone(bar(a=None))
        self.assertIsNone(bar(None))

        with self.assertRaises(expected_exception=ParameterException):
            bar('no_email')

    def test_allow_renaming_of_parameter_of_custom_validator(self) -> None:
        class MyCustomValidator(Validator):
            def validate(self, i_renamed_this_arg: Any) -> Any:
                return i_renamed_this_arg

        @validate(Parameter(name='a', validators=[MyCustomValidator()]))
        def bar(a: int):
            return a

        self.assertEqual(42, bar(42))
        self.assertEqual(42, bar(a=42))

    def test_none_is_removed_for_not_required_parameter(self) -> None:
        @validate(Parameter(name='a', required=False))
        def bar(a: int = 42):
            return a

        self.assertEqual(42, bar())
        self.assertEqual(2, bar(a=2))
        self.assertEqual(2, bar(2))

    def test_default_value_is_not_validated_internal_parameter(self) -> None:
        t = datetime(year=2021, month=11, day=24)
        unix_timestamp = (t - datetime(year=1970, month=1, day=1)).total_seconds()

        @validate(Parameter(name='a', required=False, default=t, validators=[DateTimeUnixTimestamp()]))
        def bar(a: datetime) -> datetime:
            return a

        self.assertEqual(t, bar(a=unix_timestamp))
        self.assertEqual(t, bar())

    def test_no_default_value(self) -> None:
        @validate(Parameter(name='a', required=False))
        def bar(a: datetime) -> datetime:
            return a

        with self.assertRaises(expected_exception=ValidateException):
            bar()

    def test_default_value_is_not_validated_external_parameter(self) -> None:
        t = datetime(year=2021, month=11, day=24)

        if 'a' in os.environ:
            del os.environ['a']

        @validate(EnvironmentVariableParameter(name='a', default=t, validators=[DateTimeUnixTimestamp()], required=False))
        def bar(a: datetime) -> datetime:
            return a

        self.assertEqual(t, bar())


if sys.version_info >= (3, 8):
    # IsolatedAsyncioTestCase exists since Python 3.8


    class AsyncValidateTests(IsolatedAsyncioTestCase):
        async def test_async_instance_method(self) -> None:
            class Foo:
                @validate(Parameter(name='k', value_type=int, validators=[Min(42)]))
                async def bar(self, k):
                    return k

            f = Foo()
            res = await f.bar(k=42)
            self.assertEqual(42, res)

            with self.assertRaises(expected_exception=ParameterException):
                await f.bar(k=41)
