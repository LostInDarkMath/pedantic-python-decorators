import asyncio
import time
import unittest
from typing import NoReturn

from multiprocess import Pipe

from pedantic import in_subprocess
from pedantic.decorators.fn_deco_in_subprocess import _inner, SubprocessError


class TestInSubprocess(unittest.IsolatedAsyncioTestCase):
    async def test_in_subprocess_simple(self):
        @in_subprocess
        def f() -> int:
            return 42

        assert await f() == 42

    async def test_in_subprocess_custom_object(self):
        class Foo:
            def __init__(self, v) -> None:
                self._value = v

        @in_subprocess
        def f() -> Foo:
            return Foo(v=42)

        assert (await f())._value == 42

    async def test_in_subprocess_simple_async(self):
        @in_subprocess
        async def f() -> int:
            return 42

        assert await f() == 42

    async def test_in_subprocess_no_args(self):
        @in_subprocess
        def f() -> int:
            time.sleep(0.1)
            return 42

        async def t() -> None:
            for _ in range(6):
                await asyncio.sleep(0.01)
                nonlocal counter
                counter += 1

        counter = 0
        task = asyncio.create_task(t())
        assert await f() == 42
        assert counter >= 5
        await task

    async def test_in_subprocess_no_args_no_return(self):
        @in_subprocess
        def f() -> None:
            time.sleep(0.1)

        assert await f() is None

    async def test_in_subprocess_exception(self):
        @in_subprocess
        def f() -> NoReturn:
            raise RuntimeError('foo')

        with self.assertRaises(expected_exception=RuntimeError):
            await f()

    async def test_not_in_subprocess_blocks(self):
        async def f() -> int:
            time.sleep(0.1)
            return 42

        async def t() -> None:
            for _ in range(6):
                await asyncio.sleep(0.05)
                nonlocal counter
                counter += 1

        counter = 0
        task = asyncio.create_task(t())
        assert await f() == 42
        assert counter == 0
        await task

    async def test_in_subprocess_with_arguments(self):
        @in_subprocess
        def f(a: int, b: int) -> int:
            return a + b

        assert await f(4, 5) == 9
        assert await f(a=4, b=5) == 9

    def test_inner_function_sync(self):
        """ Needed for line coverage"""

        rx, tx = Pipe(duplex=False)
        _inner(tx, lambda x: 1 / x, x=42)
        assert rx.recv() == 1 / 42

        _inner(tx, lambda x: 1 / x, x=0)
        ex = rx.recv()
        assert isinstance(ex, SubprocessError)

    def test_inner_function_async(self):
        """ Needed for line coverage"""

        async def foo(x):
            return 1/x

        rx, tx = Pipe(duplex=False)
        _inner(tx, foo, x=42)
        assert rx.recv() == 1 / 42

        _inner(tx, foo, x=0)
        ex = rx.recv()
        assert isinstance(ex, SubprocessError)

    async def test_in_subprocess_instance_method(self):
        class Foo:
            async def pos_args(self) -> int:
                return await self.f(4, 5)

            async def kw_args(self) -> int:
                return await self.f(a=4, b=5)

            @in_subprocess
            def f(self, a: int, b: int) -> int:
                return a + b

        foo = Foo()
        assert await foo.pos_args() == 9
        assert await foo.kw_args() == 9

    async def test_in_subprocess_static_method(self):
        class Foo:
            async def pos_args(self) -> int:
                return await self.f(4, 5)

            async def kw_args(self) -> int:
                return await self.f(a=4, b=5)

            @staticmethod
            @in_subprocess
            def f(a: int, b: int) -> int:
                return a + b

        foo = Foo()
        assert await foo.pos_args() == 9
        assert await foo.kw_args() == 9
