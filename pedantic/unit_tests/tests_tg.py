import unittest
from typing import TypeVar, Generator, Iterator, Iterable, NoReturn

from pedantic import pedantic_class
from pedantic.exceptions import PedanticTypeCheckException, PedanticTypeVarMismatchException
from pedantic.method_decorators import pedantic


class TestDecoratorRequireKwargsAndTypeCheck(unittest.TestCase):
    def test_pedantic(self):
        @pedantic
        def foo(a: int, b: str) -> str:
            return 'abc'

        self.assertEqual('abc', foo(a=4, b='abc'))

    def test_pedantic_always(self):
        @pedantic
        def foo(a: int, b: str) -> str:
            return 'abc'

        self.assertEqual('abc', foo(a=4, b='abc'))

    def test_pedantic_arguments_fail(self):
        @pedantic
        def foo(a: int, b: str) -> str:
            return 'abc'

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            foo(a=4, b=5)

    def test_pedantic_return_type_fail(self):
        @pedantic
        def foo(a: int, b: str) -> str:
            return 6

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            foo(a=4, b='abc')

    def test_pedantic_return_typevar_fail(self):
        T = TypeVar('T', int, float)

        @pedantic
        def foo(a: T, b: T) -> T:
            return 'a'

        with self.assertRaises(expected_exception=PedanticTypeVarMismatchException):
            foo(a=4, b=2)

    def test_return_type_none(self):
        @pedantic
        def foo() -> None:
            return 'a'

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            foo()

    def test_coroutine_correct_return_type(self):
        @pedantic
        async def foo() -> str:
            return 'foo'

        foo()

    # def test_coroutine_wrong_return_type(self):
    #     @pedantic
    #     async def foo() -> str:
    #         return 1
    #
    #     with self.assertRaises(expected_exception=PedanticTypeCheckException):
    #         foo()

    def test_class_decorator(self):
        @pedantic_class
        class Foo:
            @staticmethod
            def staticmethod() -> int:
                return 'foo'

            @classmethod
            def classmethod(cls) -> int:
                return 'foo'

            def method(self) -> int:
                return 'foo'

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            Foo.staticmethod()
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            Foo.classmethod()
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            Foo().method()

    def test_iterator(self):
        @pedantic
        def genfunc() -> Iterator[int]:
            num = 0

            while num < 100:
                yield num
                num += 1

        gen = genfunc()
        next(gen)

    def test_iterable(self):
        @pedantic
        def genfunc() -> Iterable[int]:
            num = 0

            while num < 100:
                yield num
                num += 1

        gen = genfunc()
        next(gen)

    def test_generator(self):
        @pedantic
        def genfunc() -> Generator[int, None, str]:
            num = 0

            while num < 100:
                yield num
                num += 1
            return 'Done'

        gen = genfunc()
        next(gen)
