import unittest
from abc import ABC, abstractmethod

from pedantic.decorators.class_decorators import pedantic_class, for_all_methods
from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.validators import Min
from pedantic.exceptions import PedanticException, PedanticTypeCheckException, PedanticCallWithArgsException
from pedantic.decorators.fn_deco_pedantic import pedantic
from pedantic import overrides
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate, Parameter


class TestCombinationOfDecorators(unittest.TestCase):
    def test_pedantic_overrides(self):
        class MyClass(ABC):
            @pedantic
            @abstractmethod
            def op(self, a: int) -> None:
                pass

        class Child(MyClass):
            a = 0

            @pedantic
            @overrides(MyClass)
            def op(self, a: int) -> None:
                self.a = a

        c = Child()
        c.op(a=42)

    def test_pedantic_below_validate(self):
        @validate(
            Parameter(name='x', validators=[Min(0)]),
        )
        @pedantic
        def some_calculation(x: int) -> int:
            return x

        some_calculation(x=42)
        some_calculation(42)

        with self.assertRaises(expected_exception=ParameterException):
            some_calculation(x=-1)
        with self.assertRaises(expected_exception=ParameterException):
            some_calculation(x=-42)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            some_calculation(x=1.0)

    def test_pedantic_above_validate(self):
        @pedantic
        @validate(
            Parameter(name='x', validators=[Min(0)]),
        )
        def some_calculation(x: int) -> int:
            return x

        some_calculation(x=42)

        with self.assertRaises(expected_exception=ParameterException):
            some_calculation(x=-1)
        with self.assertRaises(expected_exception=ParameterException):
            some_calculation(x=-42)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            some_calculation(x=1.0)
        with self.assertRaises(expected_exception=PedanticException):
            some_calculation(42)

    def test_pedantic_above_validate_on_instance_method(self):
        class MyClass:
            @pedantic
            @validate(
                Parameter(name='x', validators=[Min(0)]),
            )
            def some_calculation(self, x: int) -> int:
                return x

        m = MyClass()
        m.some_calculation(x=42)
        with self.assertRaises(expected_exception=ParameterException):
            m.some_calculation(x=-1)
        with self.assertRaises(expected_exception=ParameterException):
            m.some_calculation(x=-42)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            m.some_calculation(x=1.0)
        with self.assertRaises(expected_exception=PedanticCallWithArgsException):
            m.some_calculation(42)

    def test_pedantic_below_validate_on_instance_method(self):
        class MyClass:
            @validate(
                Parameter(name='x', validators=[Min(0)]),
            )
            @pedantic
            def some_calculation(self, x: int) -> int:
                return x

        m = MyClass()
        m.some_calculation(x=42)
        m.some_calculation(42)

        with self.assertRaises(expected_exception=ParameterException):
            m.some_calculation(x=-1)
        with self.assertRaises(expected_exception=ParameterException):
            m.some_calculation(x=-42)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            m.some_calculation(x=1.0)

    def test_pedantic_class_with_validate_instance_method(self):
        @pedantic_class
        class MyClass:
            @validate(
                Parameter(name='x', validators=[Min(0)]),
            )
            def some_calculation(self, x: int) -> int:
                return x

        m = MyClass()
        m.some_calculation(x=42)
        with self.assertRaises(expected_exception=ParameterException):
            m.some_calculation(x=-1)
        with self.assertRaises(expected_exception=ParameterException):
            m.some_calculation(x=-42)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            m.some_calculation(x=1.0)
        with self.assertRaises(expected_exception=PedanticCallWithArgsException):
            m.some_calculation(42)

    def test_pedantic_class_static_method_1(self):
        @pedantic_class
        class MyClass:
            @staticmethod
            def some_calculation(x: int) -> int:
                return x

        m = MyClass()
        m.some_calculation(x=42)
        MyClass.some_calculation(x=45)

    def test_pedantic_class_static_method_2(self):
        """Never do this, but it works"""
        @for_all_methods(staticmethod)
        @pedantic_class
        class MyClass:
            def some_calculation(x: int) -> int:
                return x

        m = MyClass()
        m.some_calculation(x=42)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            m.some_calculation(x=42.0)
        MyClass.some_calculation(x=45)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            MyClass.some_calculation(x=45.0)

    def test_pedantic_static_method_1(self):
        class MyClass:
            @staticmethod
            @pedantic
            def some_calculation(x: int) -> int:
                return x

        m = MyClass()
        m.some_calculation(x=42)
        MyClass.some_calculation(x=45)
