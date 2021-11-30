import inspect
from datetime import datetime
from functools import wraps
from typing import Any

from pedantic.constants import F, ReturnType


def trace(func: F) -> F:
    """
       Prints the passed arguments and the returned value on each function call.

       Example:

       >>> @trace
       ... def my_function(a, b, c):
       ...     return a + b + c
       >>> my_function(4, 5, 6)
       Trace: ... calling my_function()  with (4, 5, 6), {}
       Trace: ... my_function() returned 15
       15
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
        print(f'Trace: {datetime.now()} calling {func.__name__}()  with {args}, {kwargs}')
        original_result = func(*args, **kwargs)
        print(f'Trace: {datetime.now()} {func.__name__}() returned {original_result!r}')
        return original_result

    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> ReturnType:
        print(f'Trace: {datetime.now()} calling {func.__name__}()  with {args}, {kwargs}')
        original_result = await func(*args, **kwargs)
        print(f'Trace: {datetime.now()} {func.__name__}() returned {original_result!r}')
        return original_result

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return wrapper


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
