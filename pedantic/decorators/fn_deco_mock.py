import inspect
from functools import wraps
from typing import Any

from pedantic.constants import ReturnType, F


def mock(return_value: ReturnType) -> F:
    """
        Skip the execution of the function and simply return the given return value instead.
        This can be useful you want to check quickly if the behavior of the function causes a specific problem.
        Without this decorator you actually need to change the implementation of the function temporarily.

        Example:

        >>> @mock(return_value=42)
        ... def my_function(a, b, c):
        ...     return a + b + c
        >>> my_function(1, 2, 3)
        42
        >>> my_function(1000, 88, 204)
        42
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            return return_value

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            return return_value

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
    return decorator


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
