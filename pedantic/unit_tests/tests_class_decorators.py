import unittest

# local file imports
from pedantic.class_decorators import pedantic_class, pedantic_class_require_docstring, trace_class, timer_class


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
                res = f'{self.a} and {s}'

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
                res = f'{self.a} and {s}'

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
                res = f'{self.a} and {s}'

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
                res = f'{self.a} and {s}'

        with self.assertRaises(expected_exception=AssertionError):
            m = MyClass(a=5)
            m.calc(b=42)
            m.print('Hi')

    def test_generator_1(self):
        """Problem here: typo in type annotation string"""
        @pedantic_class
        class MyClass:
            def __init__(self, s: str) -> None:
                self.s = s

            def double(self, b: int) -> str:
                return self.s + str(b)

            @staticmethod
            def generator() -> 'MyClas':
                return MyClass(s='generated')

        with self.assertRaises(expected_exception=AssertionError):
            m = MyClass.generator()
            m.double(b=42)

    def test_generator_1_corrected(self):
        @pedantic_class
        class MyClass:
            def __init__(self, s: str) -> None:
                self.s = s

            def double(self, b: int) -> str:
                return self.s + str(b)

            @staticmethod
            def generator() -> 'MyClass':
                return MyClass(s='generated')

        m = MyClass.generator()
        m.double(b=42)

    def test_pedanti_class_require_docstring(self):
        @pedantic_class_require_docstring
        class MyClass:
            def __init__(self, s: str) -> None:
                """Constructor

                Args:
                    s (str): name
                """
                self.s = s

            def double(self, b: int) -> str:
                """some method

                Args:
                    b (int): magic number

                Returns:
                    str: cool stuff

                """
                return self.s + str(b)

            @staticmethod
            def generator() -> 'MyClass':
                """Static

                Returns:
                    MyClass: instance
                """
                return MyClass(s='generated')

        m = MyClass.generator()
        m.double(b=42)

    def test_pedantic_class_require_docstring_1(self):
        """Problem here: Typo in type annotation string"""
        @pedantic_class_require_docstring
        class MyClass:
            def __init__(self, s: str) -> None:
                """Constructor

                Args:
                    s (str): name
                """
                self.s = s

            def double(self, b: int) -> str:
                """some method

                Args:
                    b (int): magic number

                Returns:
                    str: cool stuff

                """
                return self.s + str(b)

            @staticmethod
            def generator() -> 'MyClas':
                """Static

                Returns:
                    MyClass: instance
                """
                return MyClass(s='generated')

        with self.assertRaises(expected_exception=AssertionError):
            m = MyClass.generator()
            m.double(b=42)

    def test_pedantic_class_require_docstring_2(self):
        """Problem here: Typo in docstring corresponding to type annotation string"""
        @pedantic_class_require_docstring
        class MyClass:
            def __init__(self, s: str) -> None:
                """Constructor

                Args:
                    s (str): name
                """
                self.s = s

            def double(self, b: int) -> str:
                """some method

                Args:
                    b (int): magic number

                Returns:
                    str: cool stuff

                """
                return self.s + str(b)

            @staticmethod
            def generator() -> 'MyClass':
                """Static

                Returns:
                    MyClas: instance
                """
                return MyClass(s='generated')

        with self.assertRaises(expected_exception=AssertionError):
            m = MyClass.generator()
            m.double(b=42)

    def test_pedantic_class_require_docstring_3(self):
        """Problem here: One docstring is wrong"""
        @pedantic_class_require_docstring
        class MyClass:
            def __init__(self, s: str) -> None:
                """Constructor

                Args:
                    s (str): name
                """
                self.s = s

            def double(self, b: int) -> str:
                """some method

                Args:
                    b (float): magic number

                Returns:
                    str: cool stuff

                """
                return self.s + str(b)

            @staticmethod
            def generator() -> 'MyClass':
                """Static

                Returns:
                    MyClass: instance
                """
                return MyClass(s='generated')

        with self.assertRaises(expected_exception=AssertionError):
            m = MyClass.generator()
            m.double(b=42)

    def test_trace_class(self):
        @trace_class
        class MyClass:
            def __init__(self, s: str) -> None:
                self.s = s

            def double(self, b: int) -> str:
                return self.s + str(b)

            @staticmethod
            def generator() -> 'MyClass':
                return MyClass(s='generated')

        m = MyClass.generator()
        m.double(b=42)

    def test_timer_class(self):
        @timer_class
        class MyClass:
            def __init__(self, s: str) -> None:
                self.s = s

            def double(self, b: int) -> str:
                return self.s + str(b)

            @staticmethod
            def generator() -> 'MyClass':
                return MyClass(s='generated')

        m = MyClass.generator()
        m.double(b=42)
