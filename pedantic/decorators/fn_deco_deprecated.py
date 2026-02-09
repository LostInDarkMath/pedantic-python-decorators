import warnings
from functools import wraps
from typing import Any, Callable, overload

from pedantic.constants import F, ReturnType

@overload
def deprecated(func: F) -> F: ...

@overload
def deprecated(*, message: str = '') -> Callable[[F], F]: ...

def deprecated(func: F | None = None, message: str = '') -> F | Callable[[F], F]:
    """
        Use this decorator to mark a function as deprecated. It will raise a warning when the function is called.
        You can specify an optional reason or message to display with the warning.

        Example:
        >>> @deprecated
        ... def my_function(a, b, c):
        ...     pass
        >>> my_function(5, 4, 3)  # doctest: +SKIP
        >>> @deprecated(message='Will be removed soon. Please use my_function_new_instead.')
        ... def my_function(a, b, c):
        ...     pass
        >>> my_function(5, 4, 3)  # doctest: +SKIP
    """

    def decorator(fun: F) -> F:
        @wraps(fun)
        def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            msg = f'Call to deprecated function {fun.__qualname__}.'

            if message:
                msg += f'\nReason: {message}'

            warnings.warn(message=msg, category=DeprecationWarning, stacklevel=2)
            return fun(*args, **kwargs)
        return wrapper
    return decorator if func is None else decorator(func)
