import inspect
from functools import wraps
from typing import Any

from pedantic.constants import F, ReturnType


def does_same_as_function(other_func: F) -> F:
    """
        Each time the decorated function is executed, the function other_func is also executed and the results
        are compared. An AssertionError is raised if the results are not equal.

        Example:

        >>> def other_calculation(a, b, c):
        ...     return c + b + a
        >>> @does_same_as_function(other_calculation)
        ... def some_calculation(a, b, c):
        ...     return a + b + c
        >>> some_calculation(1, 2, 3)
        6
    """

    def decorator(decorated_func: F) -> F:
        @wraps(decorated_func)
        def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            result = decorated_func(*args, **kwargs)
            other = other_func(*args, **kwargs)

            if other != result:
                raise AssertionError(f'Different outputs: Function "{decorated_func.__name__}" returns {result} and '
                                     f'function "{other_func.__name__}" returns {other} for parameters {args} {kwargs}')
            return result

        @wraps(decorated_func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            result = await decorated_func(*args, **kwargs)

            if inspect.iscoroutinefunction(other_func):
                other = await other_func(*args, **kwargs)
            else:
                other = other_func(*args, **kwargs)

            if other != result:
                raise AssertionError(f'Different outputs: Function "{decorated_func.__name__}" returns {result} and '
                                     f'function "{other_func.__name__}" returns {other} for parameters {args} {kwargs}')
            return result

        if inspect.iscoroutinefunction(decorated_func):
            return async_wrapper
        else:
            return wrapper

    return decorator


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
