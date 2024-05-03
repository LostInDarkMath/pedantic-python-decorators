import logging
import time
from datetime import timedelta
from functools import wraps
from logging import Logger
from typing import Callable, TypeVar, Any, ParamSpec

C = TypeVar('C', bound=Callable)
P = ParamSpec('P')
R = TypeVar('R')


def retry(
    *,
    attempts: int,
    exceptions: type[Exception] | tuple[type[Exception], ...] = Exception,
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

    def decorator(func: C) -> C:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return retry_func(
                func,
                *args,
                attempts=attempts,
                exceptions=exceptions,
                sleep_time=sleep_time,
                logger=logger,
                **kwargs,
            )
        return wrapper
    return decorator


def retry_func(
    func: Callable[P, R],
    *args: P.args,
    attempts: int,
    exceptions: type[Exception] | tuple[type[Exception], ...] = Exception,
    sleep_time: timedelta = timedelta(seconds=0),
    logger: Logger = None,
    **kwargs: P.kwargs,
) -> R:
    attempt = 1

    if logger is None:
        logger = logging.getLogger()

    while attempt < attempts:
        try:
            return func(*args, **kwargs)
        except exceptions:
            logger.warning(f'Exception thrown when attempting to run {func.__name__}, '
                           f'attempt {attempt} of {attempts}')
            attempt += 1
            time.sleep(sleep_time.total_seconds())

    return func(*args, **kwargs)
