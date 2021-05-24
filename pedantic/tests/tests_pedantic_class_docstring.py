import unittest

from pedantic import pedantic_class_require_docstring
from pedantic.exceptions import PedanticDocstringException


class TestPedanticClassDocstring(unittest.TestCase):
    def test_require_docstring(self):
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

    def test_typo_docstring(self):
        with self.assertRaises(expected_exception=PedanticDocstringException):
            @pedantic_class_require_docstring
            class MyClass:
                def __init__(self, s: str) -> None:
                    """Constructor

                    Args:
                        s (str): name
                    """
                    self.s = s

                @staticmethod
                def generator() -> 'MyClass':
                    """Static

                    Returns:
                        MyClas: instance
                    """
                    return MyClass(s='generated')

    def test_wrong_docstring(self):
        with self.assertRaises(expected_exception=PedanticDocstringException):
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
