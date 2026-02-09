import asyncio

import pytest

from pedantic import trace, trace_if_returns, require_kwargs
from pedantic.exceptions import PedanticCallWithArgsException


def test_trace():
    def some_method(x, y):
        return x + y

    traced_method = trace(some_method)
    assert some_method(42, 99) == traced_method(42, 99)


def test_trace_if_returns():
    def some_method(x, y):
        return x + y
    
    traced_method = trace_if_returns(100)(some_method)
    assert some_method(42, 99) == traced_method(42, 99)
    assert some_method(42, 58) == traced_method(42, 58)


@pytest.mark.asyncio
async def test_trace_async():
    async def some_method(x, y):
        await asyncio.sleep(0)
        return x + y

    traced_method = trace(some_method)
    assert await some_method(42, 99) == await traced_method(42, 99)


@pytest.mark.asyncio
async def test_trace_if_returns_async():
    async def some_method(x, y):
        await asyncio.sleep(0)
        return x + y

    traced_method = trace_if_returns(100)(some_method)
    assert await some_method(42, 99) == await traced_method(42, 99)
    assert await some_method(42, 58), await traced_method(42, 58)


@pytest.mark.asyncio
async def test_require_kwargs():
    @require_kwargs
    async def calc(n: int, m: int, i: int) -> int:
        return n + m + i

    await calc(n=1, m=2, i=3)

    with pytest.raises(expected_exception=PedanticCallWithArgsException):
        await calc(1, m=2, i=3)
