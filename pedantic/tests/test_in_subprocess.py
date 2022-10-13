import asyncio
import time
import unittest

from pedantic import in_subprocess


class TestInSubprocess(unittest.IsolatedAsyncioTestCase):
    async def test_in_subprocess_simple(self):
        @in_subprocess
        def f() -> int:
            return 42

        assert await f() == 42

    def test_in_subprocess_simple_async(self):
        with self.assertRaises(expected_exception=AssertionError):
            @in_subprocess
            async def f() -> int:
                return 42

    async def test_in_subprocess_no_args(self):
        @in_subprocess
        def f() -> int:
            time.sleep(0.1)
            return 42

        async def t() -> None:
            while True:
                await asyncio.sleep(0.01)
                nonlocal counter
                counter += 1

        counter = 0
        task = asyncio.create_task(t())
        assert await f() == 42
        assert counter >= 5
        task.cancel()

    async def test_not_in_subprocess_blocks(self):
        async def f() -> int:
            time.sleep(0.1)
            return 42

        async def t() -> None:
            while True:
                await asyncio.sleep(0.05)
                nonlocal counter
                counter += 1

        counter = 0
        task = asyncio.create_task(t())
        assert await f() == 42
        assert counter == 0
        task.cancel()

    async def test_in_subprocess_with_arguments(self):
        @in_subprocess
        def f(a: int, b: int) -> int:
            return a + b

        assert await f(4, 5) == 9
        assert await f(a=4, b=5) == 9
        