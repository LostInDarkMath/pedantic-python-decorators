import asyncio
import os
import signal
import struct
import time
from importlib import import_module
from types import SimpleNamespace
from typing import NoReturn
from unittest.mock import MagicMock

import multiprocess
import pytest
from multiprocess import Pipe

from pedantic import calculate_in_subprocess, in_subprocess
from pedantic.decorators.in_subprocess import SubprocessError, _inner

main = import_module('pedantic.decorators.in_subprocess')


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


@pytest.mark.parametrize('x', [42, 0])
def test_inner_function_sync(x):
    """Needed for line coverage"""

    rx, tx = Pipe(duplex=False)
    try:
        _inner(tx, lambda x: 1 / x, x=x)
        result = rx.recv()
        if x:
            assert result == 1 / x
        else:
            assert isinstance(result.exception, ZeroDivisionError)
        assert tx.closed
    finally:
        rx.close()


@pytest.mark.parametrize('x', [42, 0])
def test_inner_function_async(x):
    """Needed for line coverage"""

    async def foo(x):
        return 1/x

    rx, tx = Pipe(duplex=False)
    try:
        _inner(tx, foo, x=x)
        result = rx.recv()
        if x:
            assert result == 1 / x
        else:
            assert isinstance(result.exception, ZeroDivisionError)
        assert tx.closed
    finally:
        rx.close()
        asyncio.set_event_loop(None)


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


@pytest.fixture
def subprocess_mocks(monkeypatch):
    rx = MagicMock()
    tx = MagicMock()
    rx.fileno.return_value = 123
    rx.poll.return_value = True
    rx.recv.return_value = 42
    process = MagicMock()
    process.pid = 1
    process.sentinel = 456
    process.exitcode = 0
    process.is_alive.return_value = False
    loop = MagicMock()

    def add_reader(fd, callback):
        if fd == process.sentinel:
            callback()

    loop.add_reader.side_effect = add_reader
    monkeypatch.setattr(main, 'Pipe', MagicMock(return_value=(rx, tx)))
    monkeypatch.setattr(main, 'Process', MagicMock(return_value=process))
    monkeypatch.setattr(main, 'asyncio', SimpleNamespace(
        get_running_loop=lambda: loop,
        Event=asyncio.Event,
        to_thread=asyncio.to_thread,
    ))
    return rx, tx, process, loop


@pytest.mark.asyncio
@pytest.mark.parametrize('already_available', [True, False])
async def test_in_subprocess_result_available(subprocess_mocks, already_available):
    rx, tx, process, loop = subprocess_mocks
    rx.poll.side_effect = [already_available, True]
    assert await calculate_in_subprocess(lambda: 42) == 42
    rx.recv.assert_called_once_with()
    process.start.assert_called_once_with()
    process.join.assert_called_once_with()
    process.close.assert_called_once_with()
    rx.close.assert_called_once_with()
    assert tx.close.call_count == 2
    assert loop.remove_reader.call_args_list == [((123,),), ((456,),)]


@pytest.mark.asyncio
@pytest.mark.parametrize('failure', ['no_data', 'eof', 'oserror', 'exitcode', 'remote'])
async def test_subprocess_failures_cleanup(subprocess_mocks, failure):
    rx, tx, process, loop = subprocess_mocks
    expected = ChildProcessError
    if failure == 'no_data':
        rx.poll.return_value = False
    elif failure == 'eof':
        rx.recv.side_effect = EOFError('closed')
    elif failure == 'oserror':
        rx.recv.side_effect = OSError('broken pipe')
    elif failure == 'exitcode':
        process.exitcode = 7
    else:
        rx.recv.return_value = SubprocessError(ValueError('remote error'))
        expected = ValueError
    with pytest.raises(expected):
        await calculate_in_subprocess(lambda: 42)
    rx.close.assert_called_once_with()
    assert tx.close.call_count == 2
    process.close.assert_called_once_with()
    assert loop.remove_reader.call_count == 2


@pytest.mark.asyncio
@pytest.mark.parametrize('failure', ['construct', 'start', 'reader'])
async def test_subprocess_setup_failure_cleanup(subprocess_mocks,  failure):
    rx, tx, process, loop = subprocess_mocks
    if failure == 'construct':
        main.Process.side_effect = RuntimeError('setup failed')
    elif failure == 'start':
        process.pid = None
        process.start.side_effect = RuntimeError('setup failed')
    else:
        loop.add_reader.side_effect = RuntimeError('setup failed')
    with pytest.raises(RuntimeError, match='setup failed'):
        await calculate_in_subprocess(lambda: 42)
    rx.close.assert_called_once_with()
    tx.close.assert_called()
    if failure != 'construct':
        process.close.assert_called_once_with()
    else:
        process.close.assert_not_called()
    if failure == 'reader':
        assert loop.remove_reader.call_count == 2


@pytest.mark.asyncio
@pytest.mark.parametrize('needs_kill', [False, True])
async def test_subprocess_cleanup_escalation(subprocess_mocks, needs_kill):
    rx, tx, process, loop = subprocess_mocks
    loop.add_reader.side_effect = RuntimeError('reader failed')
    process.is_alive.side_effect = [True, needs_kill]
    with pytest.raises(RuntimeError, match='reader failed'):
        await calculate_in_subprocess(lambda: 42)
    process.terminate.assert_called_once_with()
    assert process.kill.call_count == int(needs_kill)
    assert process.join.call_count == 1 + int(needs_kill)
    for call in process.join.call_args_list:
        assert call.kwargs == {'timeout': 1}
    process.close.assert_called_once_with()
    rx.close.assert_called_once_with()
    tx.close.assert_called()


@pytest.mark.asyncio
async def test_missing_multiprocess(monkeypatch):
    monkeypatch.setattr(main, 'Pipe', None)
    with pytest.raises(ImportError, match='multiprocess'):
        await calculate_in_subprocess(lambda: 42)


def test_inner_serialization_failure():
    tx = MagicMock()
    error = AttributeError('serialization failed')
    tx.send.side_effect = [error, None]
    _inner(tx, lambda: 42)
    assert tx.send.call_args_list[0].args == (42,)
    assert tx.send.call_args_list[1].args[0].exception is error
    tx.close.assert_called_once_with()


def test_inner_error_cannot_be_serialized():
    tx = MagicMock()
    tx.send.side_effect = TypeError('cannot serialize')
    with pytest.raises(TypeError, match='cannot serialize'):
        _inner(tx, lambda: 42)
    assert tx.send.call_count == 2
    tx.close.assert_called_once_with()


def test_inner_event_loop_closed(monkeypatch):
    loop = asyncio.new_event_loop()
    monkeypatch.setattr(asyncio, 'new_event_loop', lambda: loop)
    monkeypatch.setattr(asyncio, 'set_event_loop', MagicMock())
    tx = MagicMock()

    async def f():
        return 42

    _inner(tx, f)
    assert loop.is_closed()
    tx.close.assert_called_once_with()


@pytest.mark.asyncio
async def test_subprocess_abrupt_exit():
    with pytest.raises(ChildProcessError):
        await asyncio.wait_for(calculate_in_subprocess(os._exit, 7), timeout=3)


@pytest.mark.asyncio
async def test_subprocess_serialization_failure():
    class Unserializable:
        def __reduce__(self):
            raise TypeError('cannot serialize result')

    with pytest.raises(TypeError, match='cannot serialize result'):
        await asyncio.wait_for(calculate_in_subprocess(Unserializable), timeout=3)


@pytest.mark.asyncio
async def test_subprocess_unserializable_error():
    class UnserializableError(Exception):
        def __reduce__(self):
            raise TypeError('cannot serialize exception')

    def f():
        raise UnserializableError('child failed')

    with pytest.raises(ChildProcessError):
        await asyncio.wait_for(calculate_in_subprocess(f), timeout=3)


@pytest.mark.asyncio
@pytest.mark.parametrize('state', ['calculating', 'partial_result', 'ignores_terminate'])
async def test_subprocess_timeout_cleanup(monkeypatch, state):
    processes = []
    pipes = []

    def create_pipe(*args, **kwargs):
        connections = Pipe(*args, **kwargs)
        pipes.extend(connections)
        return connections

    def create_process(*args, **kwargs):
        process = multiprocess.Process(*args, **kwargs)
        processes.append(process)
        return process

    def stalled_sender(tx, fun, *args, **kwargs):  # noqa: ARG001
        if state == 'partial_result':
            os.write(tx.fileno(), struct.pack('!i', 1024))
        else:
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            tx.send(42)
        time.sleep(60)

    if state != 'calculating':
        monkeypatch.setattr(main, '_inner', stalled_sender)
    monkeypatch.setattr(main, 'Pipe', create_pipe)
    monkeypatch.setattr(main, 'Process', create_process)
    with pytest.raises(TimeoutError):
        await asyncio.wait_for(calculate_in_subprocess(time.sleep, 60), timeout=0.3)
    assert len(processes) == 1
    with pytest.raises(ValueError, match='closed'):
        processes[0].is_alive()
    assert all(connection.closed for connection in pipes)


@pytest.mark.asyncio
async def test_subprocess_large_result():
    result = b'x' * (1024 * 1024)
    assert await asyncio.wait_for(calculate_in_subprocess(bytes, result), timeout=3) == result


@pytest.mark.asyncio
async def test_subprocess_cancellation_after_result(subprocess_mocks):
    rx, tx, process, loop = subprocess_mocks
    loop.add_reader.side_effect = None
    process.is_alive.side_effect = [True, False]
    with pytest.raises(TimeoutError):
        await asyncio.wait_for(calculate_in_subprocess(lambda: 42), timeout=0.1)
    rx.recv.assert_called_once_with()
    process.terminate.assert_called_once_with()
    process.close.assert_called_once_with()
    rx.close.assert_called_once_with()
    tx.close.assert_called()
    assert loop.remove_reader.call_count == 2
