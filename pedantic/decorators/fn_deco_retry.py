import logging
import time
from collections.abc import Callable
from datetime import timedelta
from functools import wraps
from logging import Logger
from typing import Any, ParamSpec, TypeVar

C = TypeVar('C', bound=Callable)
P = ParamSpec('P')
R = TypeVar('R')


def retry(
    *,
    attempts: int,
    exceptions: type[Exception] | tuple[type[Exception], ...] = Exception,
    sleep_time: timedelta = timedelta(seconds=0),
    logger: Logger | None = None,
) -> Callable[[C], C]:
    """
    Retries the wrapped function/method `attempts` times if the exceptions listed
    in [exceptions] are thrown.

    Args:
        attempts: The number of times to repeat the wrapped function/method
        exceptions: Lists of exceptions that trigger a retry attempt.
        sleep_time: The time to wait between the retry attempts.
        logger: The logger used for logging.

    Example:
        >>> @retry(attempts=3, exceptions=(ValueError, TypeError))
        ... def foo():
        ...     raise ValueError('Some error')
        >>> foo()  # doctest: +SKIP
    """

    def decorator(func: C) -> C:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
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
    logger: Logger | None = None,
    **kwargs: P.kwargs,
) -> R:
    """
    Execute a function with retry logic.

    The function ``func`` is executed and retried up to ``attempts`` times if one of the
    specified exceptions is raised. Between retries, the function waits for the
    duration defined by ``sleep_time``. A warning is logged for each failed attempt
    except for the final one.

    Args:
        func: The callable to execute.
        *args: Positional arguments forwarded to ``func``.
        attempts: Total number of attempts before the exception is allowed to
            propagate.
        exceptions: Exception type or tuple of exception types that should trigger
            a retry. Defaults to ``Exception``.
        sleep_time: Time to wait between retry attempts. Defaults to zero seconds.
        logger: Logger used to emit warnings when a retry occurs. If ``None``,
            the root logger is used.
        **kwargs: Keyword arguments forwarded to ``func``.

    Returns:
        The return value of ``func``.

    Raises:
        Exception: Re-raises the last encountered exception if all retry attempts
            fail.
    """

    attempt = 1

    if logger is None:
        logger = logging.getLogger()

    while attempt < attempts:
        try:
            return func(*args, **kwargs)
        except exceptions:
            logger.warning(f'Exception thrown when attempting to run {func.__name__}, '  # noqa: G004
                           f'attempt {attempt} of {attempts}')
            attempt += 1
            time.sleep(sleep_time.total_seconds())

    return func(*args, **kwargs)
