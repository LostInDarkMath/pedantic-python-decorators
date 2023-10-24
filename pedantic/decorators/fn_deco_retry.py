import logging
import time
from datetime import timedelta
from functools import wraps
from logging import Logger
from typing import Callable, TypeVar, TypeVarTuple, Any

C = TypeVar('C', bound=Callable)
Ts = TypeVarTuple('Ts')


def retry(
    *,
    attempts: int,
    exceptions: type[Exception] | tuple[type[Exception], ...] = None,
    sleep_time: timedelta = timedelta(seconds=0),
    logger: Logger = None,
) -> Callable[[C], C]:
    """
    Retries the wrapped function/method `attempts` times if the exceptions listed
    in [exceptions] are thrown.

    Parameters:
        attempts: The number of times to repeat the wrapped function/method
        exceptions: Lists of exceptions that trigger a retry attempt.
        sleep_time: The time to wait between the retry attempts.
        logger: The logger used for logging.

    Example:
        >>> @retry(attempts=3, exceptions=(ValueError, TypeError))
        ... def foo():
        ...     raise ValueError('Some error')
        >>> foo()
    """

    if exceptions is None:
        exceptions = Exception

    if logger is None:
        logger = logging.getLogger()

    def decorator(func: C) -> C:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 1

            while attempt < attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    logger.warning(f'Exception thrown when attempting to run {func.__name__}, '
                                   f'attempt {attempt} of {attempts}')
                    attempt += 1
                    time.sleep(sleep_time.total_seconds())
            return func(*args, **kwargs)
        return wrapper
    return decorator
