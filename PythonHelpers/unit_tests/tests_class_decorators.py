import unittest

# local file imports
from PythonHelpers.class_decorators import pedantic_class


class TestClassDecorators(unittest.TestCase):

    def test_pedantic_class_1(self):
        """Problem here: Argument 'a" in constructor doen't have a type hint"""
        @pedantic_class
        class MyClass:
            def __init__(self, a) -> None:
                self.a = a

        with self.assertRaises(expected_exception=AssertionError):
            MyClass(a=42)

    def test_pedantic_class_2(self):
        """Problem here: Constructor must have type hint 'None'"""
        @pedantic_class
        class MyClass:
            def __init__(self, a: int):
                self.a = a

        with self.assertRaises(expected_exception=AssertionError):
            MyClass(a=42)

    def test_pedantic_class_3(self):
        """Problem here: Constructor must be called with kwargs"""
        @pedantic_class
        class MyClass:
            def __init__(self, a: int) -> None:
                self.a = a

        with self.assertRaises(expected_exception=AssertionError):
            MyClass(42)

    def test_pedantic_class_1_corrected(self):
        @pedantic_class
        class MyClass:
            def __init__(self, a: int) -> None:
                self.a = a

        MyClass(a=42)

    def test_multiple_methods_1(self):
        @pedantic_class
        class MyClass:
            def __init__(self, a: int) -> None:
                self.a = a

            def calc(self, b: int) -> int:
                return self.a - b

            def print(self, s: str) -> None:
                print(f'{self.a} and {s}')

        m = MyClass(a=5)
        m.calc(b=42)
        m.print(s='Hi')

    def test_multiple_methods_2(self):
        """Problem here: missing type hints"""
        @pedantic_class
        class MyClass:
            def __init__(self, a: int) -> None:
                self.a = a

            def calc(self, b: int) -> int:
                return self.a - b

            def print(self, s: str):
                print(f'{self.a} and {s}')

        with self.assertRaises(expected_exception=AssertionError):
            m = MyClass(a=5)
            m.calc(b=42)
            m.print(s='Hi')

    def test_multiple_methods_3(self):
        """Problem here: missing type hints"""
        @pedantic_class
        class MyClass:
            def __init__(self, a: int) -> None:
                self.a = a

            def calc(self, b) -> int:
                return self.a - b

            def print(self, s: str) -> None:
                print(f'{self.a} and {s}')

        with self.assertRaises(expected_exception=AssertionError):
            m = MyClass(a=5)
            m.calc(b=42)
            m.print(s='Hi')

    def test_multiple_methods_4(self):
        """Problem here: not called with kwargs"""
        @pedantic_class
        class MyClass:
            def __init__(self, a: int) -> None:
                self.a = a

            def calc(self, b: int) -> int:
                return self.a - b

            def print(self, s: str) -> None:
                print(f'{self.a} and {s}')

        with self.assertRaises(expected_exception=AssertionError):
            m = MyClass(a=5)
            m.calc(b=42)
            m.print('Hi')
