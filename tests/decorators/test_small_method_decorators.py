import asyncio

import pytest

from pedantic import trace


def test_trace():
    def some_method(x, y):
        return x + y

    traced_method = trace(some_method)
    assert some_method(42, 99) == traced_method(42, 99)


@pytest.mark.asyncio
async def test_trace_async():
    async def some_method(x, y):
        await asyncio.sleep(0)
        return x + y

    traced_method = trace(some_method)
    assert await some_method(42, 99) == await traced_method(42, 99)
