import unittest

from pedantic import pedantic, pedantic_class
from pedantic.exceptions import PedanticTypeCheckException


class TestPedanticPython311AddedStuff(unittest.TestCase):
    def test_typing_never(self):
        from typing import Never

        @pedantic
        def never_call_me(arg: Never) -> None:
            pass

        @pedantic
        def foo() -> Never:
            pass

        @pedantic
        def bar() -> Never:
            raise ZeroDivisionError('bar')

        with self.assertRaises(expected_exception=ZeroDivisionError):
            bar()

        with self.assertRaises(PedanticTypeCheckException):
            foo()

        with self.assertRaises(expected_exception=PedanticTypeCheckException) as exc:
            never_call_me(arg='42')

    def test_literal_string(self):
        from typing import LiteralString

        @pedantic
        def foo(s: LiteralString) -> None:
            pass

        foo(s='Hi')
        foo(s=2 * 'Hi')

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            foo(s=3)

    def test_self_type(self):
        from typing import Self

        class Bar:
            pass

        @pedantic_class
        class Foo:
            def f(self) -> Self:
                return self

            @staticmethod
            def g() -> Self:
                return Foo()

            @classmethod
            def h(cls) -> Self:
                return cls()

            def f_2(self) -> Self:
                return Bar()

            @staticmethod
            def g_2() -> Self:
                return Bar()

            @classmethod
            def h_2(cls) -> Self:
                return Bar()

        f = Foo()
        assert f.f() == f
        f.g()
        f.h()
        Foo.g()
        Foo.h()

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            f.f_2()

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            f.g_2()

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            f.h_2()

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            Foo.g_2()

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            Foo.h_2()

    def test_using_self_type_annotation_outside_class(self):
        from typing import Self

        @pedantic
        def f() -> Self:
            return 'hi'

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            f()

    def test_type_var_tuple(self):
        from typing import TypeVarTuple, Generic

        Ts = TypeVarTuple('Ts')

        @pedantic_class
        class Array(Generic[*Ts]):
            def __init__(self, *args: *Ts) -> None:
                self._values = args

        @pedantic
        def add_dimension(a: Array[*Ts], value: int) -> Array[int, *Ts]:
            return Array[int, *Ts](value, *a._values)

        array = Array[int, float](42, 3.4)
        array_2 = Array[bool, int, float, str](True, 4, 3.4, 'hi')
        extended_array = add_dimension(a=array, value=42)
        assert extended_array._values == (42, 42, 3.4)

        # this is too complicated at the moment
        # with self.assertRaises(expected_exception=PedanticTypeCheckException):
        #     Array[int, float](4.2, 3.4)