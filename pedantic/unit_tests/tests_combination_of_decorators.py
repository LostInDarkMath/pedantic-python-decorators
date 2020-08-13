import unittest
from abc import ABC, abstractmethod

# local file imports
from pedantic import combine
from pedantic.method_decorators import overrides, validate_args, pedantic


class TestCombinationOfDecorators(unittest.TestCase):

    def test_pedantic_overrides(self):
        class MyClass(ABC):
            @pedantic
            @abstractmethod
            def op(self, a: int) -> None:
                pass

        class Child(MyClass):
            a = 0

            @combine([pedantic, overrides(MyClass)])
            def op(self, a: int) -> None:
                self.a = a

        c = Child()
        c.op(a=42)

    def test_pedantic_validate_args_1(self):
        @validate_args(lambda x: (x > 0, f'Argument should be greater then 0, but it was {x}.'))
        @pedantic
        def some_calculation(x: int) -> int:
            return x

        some_calculation(x=42)
        with self.assertRaises(expected_exception=AssertionError):
            some_calculation(x=0)
        with self.assertRaises(expected_exception=AssertionError):
            some_calculation(x=-42)
        with self.assertRaises(expected_exception=AssertionError):
            some_calculation(x=1.0)

    def test_pedantic_validate_args_2(self):
        @pedantic
        @validate_args(lambda x: (x > 0, f'Argument should be greater then 0, but it was {x}.'))
        def some_calculation(x: int) -> int:
            return x

        some_calculation(x=42)
        with self.assertRaises(expected_exception=AssertionError):
            some_calculation(x=0)
        with self.assertRaises(expected_exception=AssertionError):
            some_calculation(x=-42)
        with self.assertRaises(expected_exception=AssertionError):
            some_calculation(x=1.0)

    def test_pedantic_validate_args_3(self):
        class MyClass:
            @combine([pedantic, validate_args(lambda x: x > 0)])
            def some_calculation(self, x: int) -> int:
                return x

        m = MyClass()
        m.some_calculation(x=42)
        with self.assertRaises(expected_exception=AssertionError):
            m.some_calculation(x=0)
        with self.assertRaises(expected_exception=AssertionError):
            m.some_calculation(x=-42)
        with self.assertRaises(expected_exception=AssertionError):
            m.some_calculation(x=1.0)
