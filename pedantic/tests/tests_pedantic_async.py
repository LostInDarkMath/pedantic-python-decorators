import asyncio
import unittest
from typing import Any, Coroutine

from pedantic.decorators.class_decorators import pedantic_class
from pedantic.exceptions import PedanticTypeCheckException
from pedantic.decorators.fn_deco_pedantic import pedantic


class TestPedanticAsyncio(unittest.IsolatedAsyncioTestCase):
    async def test_coroutine_correct_return_type(self):
        @pedantic
        async def foo() -> str:
            await asyncio.sleep(0)
            return 'foo'

        await foo()

    async def test_coroutine_wrong_return_type(self):
        @pedantic
        async def foo() -> str:
            await asyncio.sleep(0)
            return 1

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            await foo()

    async def test_coroutine_wrong_argument_type(self):
        @pedantic
        async def foo(x: int) -> int:
            await asyncio.sleep(0)
            return 1 + x

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            await foo(x=4.5)

    async def test_static_async(self):
        @pedantic_class
        class Foo:
            @staticmethod
            async def staticmethod() -> int:
                await asyncio.sleep(0)
                return 'foo'

            @classmethod
            async def classmethod(cls) -> int:
                await asyncio.sleep(0)
                return 'foo'

            async def method(self) -> int:
                await asyncio.sleep(0)
                return 'foo'

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            await Foo.staticmethod()
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            await Foo.classmethod()
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            await Foo().method()
