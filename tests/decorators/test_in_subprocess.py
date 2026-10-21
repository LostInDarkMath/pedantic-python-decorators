import asyncio
import importlib
import time
from typing import NoReturn
from unittest.mock import MagicMock

import pytest
from multiprocess import Pipe

from pedantic import in_subprocess
from pedantic.decorators.in_subprocess import SubprocessError, _inner


@pytest.mark.asyncio
async def test_in_subprocess_simple():
    @in_subprocess
    def f() -> int:
        return 42

    assert await f() == 42


@pytest.mark.asyncio
async def test_in_subprocess_custom_object():
    class Foo:
        def __init__(self, v) -> None:
            self.value = v

    @in_subprocess
    def f() -> Foo:
        return Foo(v=42)

    assert (await f()).value == 42


@pytest.mark.asyncio
async def test_in_subprocess_simple_async():
    @in_subprocess
    async def f() -> int:
        return 42

    assert await f() == 42


@pytest.mark.asyncio
async def test_in_subprocess_no_args():
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


@pytest.mark.asyncio
async def test_in_subprocess_no_args_no_return():
    @in_subprocess
    def f() -> None:
        time.sleep(0.1)

    assert await f() is None


@pytest.mark.asyncio
async def test_in_subprocess_exception():
    @in_subprocess
    def f() -> NoReturn:
        raise RuntimeError('foo')

    with pytest.raises(expected_exception=RuntimeError):
        await f()


@pytest.mark.asyncio
async def test_not_in_subprocess_blocks():
    async def f() -> int:
        time.sleep(0.1)  # noqa: ASYNC251
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


@pytest.mark.asyncio
async def test_in_subprocess_with_arguments():
    @in_subprocess
    def f(a: int, b: int) -> int:
        return a + b

    assert await f(4, 5) == 9
    assert await f(a=4, b=5) == 9


def test_inner_function_sync():
    """Needed for line coverage"""

    rx, tx = Pipe(duplex=False)
    _inner(tx, lambda x: 1 / x, x=42)
    assert rx.recv() == 1 / 42

    _inner(tx, lambda x: 1 / x, x=0)
    ex = rx.recv()
    assert isinstance(ex, SubprocessError)


def test_inner_function_async():
    """Needed for line coverage"""

    async def foo(x):
        return 1/x

    rx, tx = Pipe(duplex=False)
    _inner(tx, foo, x=42)
    assert rx.recv() == 1 / 42

    _inner(tx, foo, x=0)
    ex = rx.recv()
    assert isinstance(ex, SubprocessError)


@pytest.mark.asyncio
async def test_in_subprocess_instance_method():
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


@pytest.mark.asyncio
async def test_in_subprocess_static_method():
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


@pytest.mark.asyncio
async def test_in_subprocess_result_already_available(monkeypatch):
    """Cover the branch where rx.poll() returns True."""
    module = importlib.import_module('pedantic.decorators.in_subprocess')

    rx = MagicMock()
    tx = MagicMock()
    rx.fileno.return_value = 123
    rx.poll.return_value = True
    rx.recv.return_value = 42

    monkeypatch.setattr(module, 'Pipe', MagicMock(return_value=(rx, tx)))

    process = MagicMock()
    monkeypatch.setattr(module, 'Process', MagicMock(return_value=process))

    loop = MagicMock()
    monkeypatch.setattr(module.asyncio, 'get_event_loop', lambda: loop)

    @module.in_subprocess
    def f() -> int:
        return 42

    assert await f() == 42

    rx.poll.assert_called_once_with()
    rx.recv.assert_called_once_with()
    process.start.assert_called_once_with()
    process.join.assert_called_once_with()
    rx.close.assert_called_once_with()
    tx.close.assert_called_once_with()

    loop.add_reader.assert_called_once_with(fd=123, callback=loop.add_reader.call_args.kwargs['callback'])
    loop.remove_reader.assert_called_once_with(fd=123)
