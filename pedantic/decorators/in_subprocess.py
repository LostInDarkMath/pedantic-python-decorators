import asyncio
import inspect
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar

try:
    from multiprocess import Pipe, Process
    from multiprocess.connection import Connection
except ImportError:
    Process: type | None = None
    Pipe: type | None = None
    Connection: type | None = None

P = ParamSpec('P')
T = TypeVar('T')


class SubprocessError:
    """Is returned by the subprocess if an error occurs in the subprocess."""

    def __init__(self, ex: Exception) -> None:  # noqa: D107
        self.exception = ex


def in_subprocess(func: Callable[P, T | Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    """
    Executes the decorated function in a subprocess and returns the return value of it.
    Note that the decorated function will be replaced with an async function which returns
    a coroutine that needs to be awaited.
    This purpose of this is doing long-taking calculations without blocking the main thread
    of your application synchronously. That ensures that other asyncio.Tasks can work without any problem
    at the same time.

    Example:
    >>> import time
    >>> import asyncio
    >>> @in_subprocess
    ... def f(value: int) -> int:
    ...     time.sleep(0.1)  # a long taking synchronous blocking calculation
    ...     return 2 * value
    >>> asyncio.run(f(value=42))
    84
    """

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return await calculate_in_subprocess(func, *args, **kwargs)

    return wrapper


async def calculate_in_subprocess(func: Callable[P, T | Awaitable[T]], *args: P.args, **kwargs: P.kwargs) -> T:  # noqa: C901
    """
    Calculates the result of a synchronous function in subprocess without blocking the current thread.

    Arguments:
        func: The function that will be called in a subprocess.
        args: Positional arguments that will be passed to the function.
        kwargs: Keyword arguments that will be passed to the function.

    Returns:
         The calculated result of the function "func".

    Raises:
        Any Exception that is raised inside [func].
        ChildProcessError: If the child exits without a result or exits unsuccessfully.

    Calls have no default time limit. Use asyncio.wait_for to impose one.
    Cancellation terminates the child and closes its pipes.

    Further reading: https://medium.com/devopss-hole/python-multiprocessing-pickle-issue-e2d35ccf96a9

    Example:
    >>> import time
    >>> import asyncio
    >>> def f(value: int) -> int:
    ...     time.sleep(0.1)  # a long taking synchronous blocking calculation
    ...     return 2 * value
    >>> asyncio.run(calculate_in_subprocess(func=f, value=42))
    84
    """

    if Pipe is None:
        raise ImportError('You need to install the multiprocess package to use this: pip install multiprocess')

    loop = asyncio.get_running_loop()
    rx, tx = Pipe(duplex=False)
    try:
        process = Process(target=_inner, args=(tx, func, *args), kwargs=kwargs)
        try:
            process.start()
            tx.close()
            ready = asyncio.Event()
            exited = asyncio.Event()

            def on_exit() -> None:
                ready.set()
                exited.set()

            try:
                loop.add_reader(rx.fileno(), ready.set)
                loop.add_reader(process.sentinel, on_exit)
                if not rx.poll():
                    await ready.wait()
                if not rx.poll():
                    raise ChildProcessError('Subprocess exited without sending a result')
                try:
                    # A readable pipe may contain only part of a large message.
                    result = await asyncio.to_thread(rx.recv)
                except (EOFError, OSError) as ex:
                    raise ChildProcessError('Subprocess pipe closed before a complete result was received') from ex
                await exited.wait()
                process.join()
                if process.exitcode != 0:
                    raise ChildProcessError(f'Subprocess exited with code {process.exitcode}')
                if isinstance(result, SubprocessError):
                    raise result.exception
                return result
            finally:
                loop.remove_reader(rx.fileno())
                loop.remove_reader(process.sentinel)
        finally:
            if process.pid is not None:  # noqa: SIM102
                if process.is_alive():
                    process.terminate()
                    await asyncio.to_thread(process.join, timeout=1)
                    if process.is_alive():
                        process.kill()
                        await asyncio.to_thread(process.join, timeout=1)
            process.close()
    finally:
        rx.close()
        tx.close()


def _inner(tx: Connection, fun: Callable[..., T | Awaitable[T]], *a: Any, **kw_args: Any) -> None:
    """This runs in another process."""

    event_loop = None
    try:
        try:
            if inspect.iscoroutinefunction(fun):
                event_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(event_loop)
                res = event_loop.run_until_complete(fun(*a, **kw_args))
            else:
                res = fun(*a, **kw_args)
            tx.send(res)
        except Exception as ex:  # noqa: BLE001
            tx.send(SubprocessError(ex=ex))
    finally:
        try:
            if event_loop is not None:
                event_loop.close()
        finally:
            tx.close()
