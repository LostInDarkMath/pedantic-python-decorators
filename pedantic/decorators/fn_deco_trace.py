import inspect
import logging
from datetime import UTC, datetime
from functools import wraps
from typing import Any

from pedantic.constants import F, ReturnType

logger = logging.getLogger(__name__)
# ruff: noqa: G004

def trace(func: F) -> F:
    """
    Prints the passed arguments and the returned value on each function call.

    Example:
    >>> @trace
    ... def my_function(a, b, c):
    ...     return a + b + c
    >>> my_function(4, 5, 6)
    15
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
        logger.info(f'Trace: {_get_now()} calling {func.__name__}()  with {args}, {kwargs}')
        original_result = func(*args, **kwargs)
        logger.info(f'Trace: {_get_now()} {func.__name__}() returned {original_result!r}')
        return original_result

    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> ReturnType:
        logger.info(f'Trace: {_get_now()} calling {func.__name__}()  with {args}, {kwargs}')
        original_result = await func(*args, **kwargs)
        logger.info(f'Trace: {_get_now()} {func.__name__}() returned {original_result!r}')
        return original_result

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return wrapper


def _get_now() -> datetime:
    return datetime.now(tz=UTC)
