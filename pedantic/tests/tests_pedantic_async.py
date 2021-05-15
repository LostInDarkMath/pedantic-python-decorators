import asyncio
import unittest
from typing import Any, Coroutine

from pedantic.decorators.class_decorators import pedantic_class
from pedantic.exceptions import PedanticTypeCheckException
from pedantic.decorators.fn_deco_pedantic import pedantic


class TestAsyncio(unittest.TestCase):
    @staticmethod
    def get_res_of_async_function(coroutine: Coroutine) -> Any:
        event_loop = asyncio.get_event_loop()
        result = event_loop.run_until_complete(future=coroutine)
        return result

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

    def test_coroutine_wrong_argument_type(self):
        @pedantic
        async def foo(x: int) -> int:
            return 1 + x

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            self.get_res_of_async_function(coroutine=foo(x=4.5))

    def test_static_async(self):
        @pedantic_class
        class Foo:
            @staticmethod
            async def staticmethod() -> int:
                return 'foo'

            @classmethod
            async def classmethod(cls) -> int:
                return 'foo'

            async def method(self) -> int:
                return 'foo'

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            self.get_res_of_async_function(Foo.staticmethod())
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            self.get_res_of_async_function(Foo.classmethod())
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            self.get_res_of_async_function(Foo().method())
