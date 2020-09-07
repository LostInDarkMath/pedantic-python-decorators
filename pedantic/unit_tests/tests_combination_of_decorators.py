import unittest
from abc import ABC, abstractmethod

# local file imports
from pedantic.class_decorators import pedantic_class, for_all_methods
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

            @pedantic
            @overrides(MyClass)
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
        @pedantic  # Different order decorators
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
            @pedantic
            @validate_args(lambda x: x > 0)
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

    def test_pedantic_validate_args_4(self):
        @pedantic_class
        class MyClass:
            @validate_args(lambda x: x > 0)
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

    def test_pedantic_validate_args_5(self):
        @pedantic
        @validate_args(lambda x: x > 0)
        def some_calculation(x: int) -> int:
            return x

        some_calculation(x=42)
        with self.assertRaises(expected_exception=AssertionError):
            some_calculation(x=0)
        with self.assertRaises(expected_exception=AssertionError):
            some_calculation(x=-42)
        with self.assertRaises(expected_exception=AssertionError):
            some_calculation(42)

    def test_pedantic_validate_args_6(self):
        class MyClass:
            @pedantic
            @validate_args(lambda x: x > 0)
            def some_calculation(self, x: int) -> int:
                return x

        m = MyClass()
        m.some_calculation(x=42)
        with self.assertRaises(expected_exception=AssertionError):
            m.some_calculation(x=0)
        with self.assertRaises(expected_exception=AssertionError):
            m.some_calculation(x=-42)
        with self.assertRaises(expected_exception=AssertionError):
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
        with self.assertRaises(expected_exception=AssertionError):
            m.some_calculation(x=42.0)
        MyClass.some_calculation(x=45)
        with self.assertRaises(expected_exception=AssertionError):
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


if __name__ == '__main__':
    t = TestCombinationOfDecorators()
    t.test_pedantic_class_static_method_1()
