from functools import wraps
from typing import Any

from pedantic.constants import F, ReturnType
from pedantic.helper_methods import _raise_warning


def deprecated(func: F) -> F:
    """
        Use this decorator to mark a function as deprecated. It will raise a warning when the function is called.

        Example:

        >>> @deprecated
        ... def my_function(a, b, c):
        ...     pass
        >>> my_function(5, 4, 3)
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
        _raise_warning(msg=f'Call to deprecated function {func.__qualname__}.', category=DeprecationWarning)
        return func(*args, **kwargs)
    return wrapper


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
