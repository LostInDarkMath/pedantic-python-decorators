from functools import wraps
from typing import Any

from pedantic.exceptions import NotImplementedException
from pedantic.constants import F, ReturnType


def unimplemented(func: F) -> F:
    """
        For documentation purposes. Throw NotImplementedException if the function is called.

        Example:

        >>> @unimplemented
        ... def my_function(a, b, c):
        ...     pass
        >>> my_function(5, 4, 3)
        Traceback (most recent call last):
        ...
        pedantic.exceptions.NotImplementedException: Function "my_function" is not implemented yet!
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
        raise NotImplementedException(f'Function "{func.__qualname__}" is not implemented yet!')
    return wrapper


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
