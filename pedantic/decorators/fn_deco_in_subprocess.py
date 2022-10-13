import asyncio
import inspect
import logging
from functools import wraps
from multiprocess import Process, Queue  # TODO add to requirements?
from typing import Callable, TypeVar, Any, Awaitable

T = TypeVar('T')


def in_subprocess(func: Callable[..., T]) -> Callable[..., Awaitable[T]]:
    """
        TODO
    """
    # TODO docu
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

        Further reading: https://medium.com/devopss-hole/python-multiprocessing-pickle-issue-e2d35ccf96a9
    """

    def f(q: Queue, fun, *a, **kw_args) -> None:
        """ This runs in another process. """

        res = fun(*a, **kw_args)
        q.put(obj=res, block=False)

    queue = Queue(maxsize=1)  # a queue with items of type T
    process = Process(target=f, args=(queue, func, *args), kwargs=kwargs)
    process.start()

    while queue.empty():  # do not use process.is_alive() as condition here
        logging.debug(process)
        logging.debug(f'Waiting for process exit...')
        await asyncio.sleep(0.1)

    result = queue.get_nowait()
    process.join()  # this blocks synchronously! make sure that process is terminated before you call join()
    logging.debug(f'Process has exited with code {process.exitcode}.')
    queue.close()
    return result
