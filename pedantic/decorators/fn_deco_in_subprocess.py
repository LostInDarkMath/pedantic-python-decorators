import asyncio
import inspect
from functools import wraps
from typing import Callable, TypeVar, Any, Awaitable, Type, Optional

try:
    from multiprocess import Process, Queue
except ImportError:
    Process: Optional[Type] = None
    Queue: Optional[Type] = None

T = TypeVar('T')


class SubprocessError:
    """ Is returned by the subprocess if an error occurs in the subprocess. """

    def __init__(self, ex: Exception) -> None:
        self.exception = ex


def in_subprocess(func: Callable[..., T]) -> Callable[..., Awaitable[T]]:
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

    if inspect.iscoroutinefunction(func):
        raise AssertionError(f'{func.__name__} should not be async!')

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        return await calculate_in_subprocess(func, *args, **kwargs)

    return wrapper


async def calculate_in_subprocess(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
        Calculates the result of a synchronous function in subprocess without blocking the current thread.

        Arguments:
            func: The synchronous function that will be called in a subprocess.
            args: Positional arguments that will be passed to the function.
            kwargs: Keyword arguments that will be passed to the function.

        Returns:
             The calculated result of the function "func".

        Raises:
            Any Exception that is raised inside [func].

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

    if Queue is None:
        raise ImportError('You need to install the multiprocess package to use this: pip install multiprocess')

    queue = Queue(maxsize=1)  # a queue with items of type T
    process = Process(target=_inner, args=(queue, func, *args), kwargs=kwargs)
    process.start()

    while queue.empty():  # do not use process.is_alive() as condition here
        await asyncio.sleep(0.1)

    result = queue.get_nowait()
    process.join()  # this blocks synchronously! make sure that process is terminated before you call join()
    queue.close()

    if isinstance(result, SubprocessError):
        raise result.exception

    return result


def _inner(q: Queue, fun: Callable[..., T], *a, **kw_args) -> None:
    """ This runs in another process. """

    try:
        res = fun(*a, **kw_args)
    except Exception as ex:
        q.put(obj=SubprocessError(ex=ex), block=False)
    else:
        q.put(obj=res, block=False)


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
