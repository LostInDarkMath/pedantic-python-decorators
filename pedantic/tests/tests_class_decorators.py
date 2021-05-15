import unittest

# local file imports
from pedantic.decorators.class_decorators import trace_class, timer_class


class TestClassDecorators(unittest.TestCase):

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
