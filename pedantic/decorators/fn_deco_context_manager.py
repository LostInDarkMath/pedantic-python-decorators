from contextlib import contextmanager, asynccontextmanager
from functools import wraps
from inspect import isasyncgenfunction, isgeneratorfunction
from typing import Callable, TypeVar, Iterator, ContextManager, AsyncContextManager, AsyncIterator

T = TypeVar('T')


def safe_contextmanager(f: Callable[..., Iterator[T]]) -> Callable[..., ContextManager[T]]:
    """
    @safe_contextmanager decorator.

    Typical usage:

        @safe_contextmanager
        def some_generator(<arguments>):
            <setup>
            yield <value>
            <cleanup>

    equivalent to this:

        @contextmanager
        def some_generator(<arguments>):
            <setup>
            try:
                yield <value>
            finally:
                <cleanup>

    This makes this:

        with some_generator(<arguments>) as <variable>:
            <body>

    equivalent to this:

        <setup>
        try:
            <variable> = <value>
            <body>
        finally:
            <cleanup>
    """

    if isasyncgenfunction(f):
        raise AssertionError(f'{f.__name__} is async. So you need to use "safe_async_contextmanager" instead.')
    if not isgeneratorfunction(f):
        raise AssertionError(f'{f.__name__} is not a generator.')

    @wraps(f)
    def wrapper(*args, **kwargs) -> Iterator[T]:
        iterator = f(*args, **kwargs)

        try:
            yield next(iterator)
        finally:
            try:
                next(iterator)
            except StopIteration:
                pass  # this is intended

    return contextmanager(wrapper)  # type: ignore


def safe_async_contextmanager(f: Callable[..., AsyncIterator[T]]) -> Callable[..., AsyncContextManager[T]]:
    """
    @safe_async_contextmanager decorator.

    Note: You need Python 3.10 or newer for this.

         Typical usage:

            @safe_async_contextmanager
            async def some_async_generator(<arguments>):
                <setup>
                yield <value>
                <cleanup>

        equivalent to this:

            @asynccontextmanager
            async def some_async_generator(<arguments>):
                <setup>
                try:
                    yield <value>
                finally:
                    <cleanup>

        This makes this:

            async with some_async_generator(<arguments>) as <variable>:
                <body>

        equivalent to this:

            <setup>
            try:
                <variable> = <value>
                <body>
            finally:
                <cleanup>
        """

    if not isasyncgenfunction(f):
        if not isgeneratorfunction(f):
            raise AssertionError(f'{f.__name__} is not a generator.')

        raise AssertionError(f'{f.__name__} is not an async generator. '
                             f'So you need to use "safe_contextmanager" instead.')

    @wraps(f)
    async def wrapper(*args, **kwargs) -> Iterator[T]:
        iterator = f(*args, **kwargs)

        try:
            yield await anext(iterator)
        finally:
            try:
                await anext(iterator)
            except StopAsyncIteration:
                pass  # this is intended

    return asynccontextmanager(wrapper)  # type: ignore
