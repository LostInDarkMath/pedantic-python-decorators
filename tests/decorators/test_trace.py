import asyncio

import pytest

from pedantic import trace


def _make_logger():
    logs: list[str] = []

    def log(msg: str) -> None:
        logs.append(msg)

    return log, logs


def test_trace_with_args():
    log, logs = _make_logger()

    @trace(log=log)
    def some_method(x, y):
        return x + y

    result = some_method(42, 99)

    assert result == 141
    assert len(logs) == 2
    assert 'some_method() with (42, 99), {}' in logs[0]
    assert 'some_method() returned 141' in logs[1]


def test_trace_with_kwargs():
    log, logs = _make_logger()

    @trace(log=log)
    def some_method(x, y):
        return x + y

    some_method(x=1, y=2)

    assert len(logs) == 2
    assert "some_method() with (), {'x': 1, 'y': 2}" in logs[0]
    assert 'some_method() returned 3' in logs[1]


def test_trace_class_logs_methods():
    log, logs = _make_logger()

    @trace(log=log)
    class SomeClass:
        def some_method(self, x, y):
            return x + y

        @staticmethod
        def some_static_method():
            return 42

        @classmethod
        def some_classmethod(cls):
            return 44

    obj = SomeClass()
    obj.some_method(42, 99)

    assert len(logs) == 2
    assert 'some_method() with' in logs[0]
    assert '42, 99), {}' in logs[0]
    assert 'some_method() returned 141' in logs[1]

    logs.clear()
    obj.some_static_method()

    assert len(logs) == 2
    assert 'some_static_method() with (), {}' in logs[0]
    assert 'some_static_method() returned 42' in logs[1]

    logs.clear()
    obj.some_classmethod()

    assert len(logs) == 2
    assert 'some_classmethod() with' in logs[0]
    assert ',), {}' in logs[0]
    assert 'some_classmethod() returned 44' in logs[1]


@pytest.mark.asyncio
async def test_trace_async_logs():
    log, logs = _make_logger()

    @trace(log=log)
    async def some_method(x, y):
        await asyncio.sleep(0)
        return x + y

    async def run():
        result = await some_method(42, 99)
        assert result == 141

    await run()

    assert len(logs) == 2
    assert 'some_method() with (42, 99), {}' in logs[0]
    assert 'some_method() returned 141' in logs[1]


def test_trace_with_no_args_no_braces():
    @trace
    def some_method(x, y):
        return x + y

    assert some_method(42, 99) == 42 + 99


def test_trace_with_no_args_with_braces():
    @trace()
    def some_method(x, y):
        return x + y

    assert some_method(42, 99) == 42 + 99


def test_trace_class_without_braces():
    @trace
    class SomeClass:
        def some_method(self, x, y):
            return x + y

    assert SomeClass().some_method(42, 99) == 42 + 99
