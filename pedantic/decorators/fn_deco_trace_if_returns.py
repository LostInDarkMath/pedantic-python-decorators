import inspect
from functools import wraps
from typing import Any

from pedantic.constants import ReturnType, F


def trace_if_returns(return_value: ReturnType) -> F:
    """
       Prints the passed arguments if and only if the decorated function returned the given return_value.
       This is useful if you want to figure out which input arguments leads to a special return value.

       Example:

       >>> @trace_if_returns(42)
       ... def my_function(a, b, c):
       ...     return a + b + c
       >>> my_function(1, 2, 3)
       6
       >>> my_function(10, 8, 24)
       Function my_function returned value 42 for args: (10, 8, 24) and kwargs: {}
       42
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            result = func(*args, **kwargs)

            if result == return_value:
                print(f'Function {func.__name__} returned value {result} for args: {args} and kwargs: {kwargs}')

            return result

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            result = await func(*args, **kwargs)

            if result == return_value:
                print(f'Function {func.__name__} returned value {result} for args: {args} and kwargs: {kwargs}')

            return result

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
    return decorator


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
