import inspect
from datetime import datetime
from functools import wraps
from typing import Any

from pedantic.constants import F, ReturnType


def timer(func: F) -> F:
    """
        Prints how long the execution of the decorated function takes.

        Example:

        >>> @timer
        ... def long_taking_calculation():
        ...     return 42
        >>> long_taking_calculation()
        Timer: Finished function "long_taking_calculation" in 0:00:00...
        42
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
        start_time: datetime = datetime.now()
        value = func(*args, **kwargs)
        end_time = datetime.now()
        run_time = end_time - start_time
        print(f'Timer: Finished function "{func.__name__}" in {run_time}.')
        return value

    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> ReturnType:
        start_time: datetime = datetime.now()
        value = await func(*args, **kwargs)
        end_time = datetime.now()
        run_time = end_time - start_time
        print(f'Timer: Finished function "{func.__name__}" in {run_time}.')
        return value

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return wrapper


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
