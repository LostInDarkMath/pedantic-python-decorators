import unittest
import asyncio
from typing import TypeVar, Generator, Iterator, Iterable, Coroutine, Any, List

from pedantic import pedantic_class
from pedantic.exceptions import PedanticTypeCheckException, PedanticTypeVarMismatchException
from pedantic.method_decorators import pedantic


class TestAsyncAndIterator(unittest.TestCase):
    @staticmethod
    def get_res_of_async_function(coroutine: Coroutine) -> Any:
        event_loop = asyncio.get_event_loop()
        result = event_loop.run_until_complete(future=coroutine)
        return result

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

        self.get_res_of_async_function(coroutine=foo())

    def test_coroutine_wrong_return_type(self):
        @pedantic
        async def foo() -> str:
            return 1

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            self.get_res_of_async_function(coroutine=foo())

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
        def gen_func() -> Iterator[int]:
            num = 0

            while num < 100:
                yield num
                num += 1

        gen = gen_func()
        next(gen)

    def test_iterator_wrong_type_hint(self):
        @pedantic
        def genfunc() -> Iterator[float]:
            num = 0

            while num < 100:
                yield num
                num += 1

        gen = genfunc()
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            next(gen)

    def test_iterator_completely_wrong_type_hint(self):
        @pedantic
        def genfunc() -> List[int]:
            num = 0

            while num < 100:
                yield num
                num += 1

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            gen = genfunc()

    def test_iterable(self):
        @pedantic
        def gen_func() -> Iterable[int]:
            num = 0

            while num < 100:
                yield num
                num += 1

        gen = gen_func()
        next(gen)

    def test_generator(self):
        @pedantic
        def gen_func() -> Generator[int, None, str]:
            num = 0

            while num < 100:
                yield num
                num += 1
            return 'Done'

        gen = gen_func()
        next(gen)
