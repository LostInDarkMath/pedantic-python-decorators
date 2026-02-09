import asyncio

import pytest

from pedantic.decorators.class_decorators import pedantic_class
from pedantic.exceptions import PedanticTypeCheckException
from pedantic.decorators.fn_deco_pedantic import pedantic


@pytest.mark.asyncio
async def test_coroutine_correct_return_type():
    @pedantic
    async def foo() -> str:
        await asyncio.sleep(0)
        return 'foo'

    await foo()


@pytest.mark.asyncio
async def test_coroutine_wrong_return_type():
    @pedantic
    async def foo() -> str:
        await asyncio.sleep(0)
        return 1

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        await foo()


@pytest.mark.asyncio
async def test_coroutine_wrong_argument_type():
    @pedantic
    async def foo(x: int) -> int:
        await asyncio.sleep(0)
        return 1 + x

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        await foo(x=4.5)


@pytest.mark.asyncio
async def test_static_async():
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

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        await Foo.staticmethod()
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        await Foo.classmethod()
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        await Foo().method()
