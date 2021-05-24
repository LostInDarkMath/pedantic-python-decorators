from datetime import datetime
from functools import wraps
from typing import Any

from pedantic.constants import F, ReturnType


def count_calls(func: F) -> F:
    """
        Prints how often the method is called during program execution.

        Example:

        >>> @count_calls
        ... def often_used_method():
        ...    return 42
        >>> often_used_method()
        Count Calls: Call 1 of function 'often_used_method' at ...
        >>> often_used_method()
        Count Calls: Call 2 of function 'often_used_method' at ...
        >>> often_used_method()
        Count Calls: Call 3 of function 'often_used_method' at ...
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
        wrapper.num_calls += 1
        print(f"Count Calls: Call {wrapper.num_calls} of function {func.__name__!r} at {datetime.now()}.")
        return func(*args, **kwargs)

    wrapper.num_calls = 0
    return wrapper


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
