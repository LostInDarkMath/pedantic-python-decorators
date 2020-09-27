import unittest
from typing import Generic, TypeVar

from pedantic.class_decorators import pedantic_class


class TestGenericClasses(unittest.TestCase):
    def test_generic_class_inheritance(self):
        class Parent:
            pass

        class Child_1(Parent):
            pass

        class Child_2(Parent):
            pass

        T = TypeVar('T')

        @pedantic_class
        class MyClass(Generic[T]):
            def __init__(self, a: T) -> None:
                self.a = a

            def get_a(self) -> T:
                return self.a

            def set_a(self, val: T) -> None:
                self.a = val

        m: MyClass[Parent] = MyClass(a=Child_1())  # a dummy comment MyClass(a=Child_3())
        self.assertTrue(isinstance(m.get_a(), Child_1))
        self.assertFalse(isinstance(m.get_a(), Child_2))
        m.set_a(val=Child_2())
        self.assertTrue(isinstance(m.get_a(), Child_2))
        self.assertFalse(isinstance(m.get_a(), Child_1))


if __name__ == '__main__':
    t = TestGenericClasses()
    t.test_generic_class_inheritance()