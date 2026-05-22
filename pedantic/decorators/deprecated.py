import warnings
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar, overload

P = ParamSpec('P')
R = TypeVar('R')
T = TypeVar('T', bound=type)


@overload
def deprecated(func: Callable[P, R]) -> Callable[P, R]: ...


@overload
def deprecated(cls: T) -> T: ...


@overload
def deprecated(
    *,
    message: str = '',
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


@overload
def deprecated(
    *,
    message: str = '',
) -> Callable[[T], T]: ...


def deprecated(
    func: Callable[P, R] | type | None = None,
    *,
    message: str = '',
) -> Any:
    """
    Use this decorator to mark a function as deprecated. It will raise a warning when the function is called.
    You can specify an optional reason or message to display with the warning.

    If you use Python 3.13 or newer, consider using warnings.deprecated instead from the standard library.

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

    def decorator(fun: Callable[P, R]) -> Callable[P, R]:
        @wraps(fun)
        def wrapper(*args: Any, **kwargs: Any) -> R:
            msg = f'Call to deprecated function {fun.__qualname__}.'

            if message:
                msg += f'\nReason: {message}'

            warnings.warn(message=msg, category=DeprecationWarning, stacklevel=2)
            return fun(*args, **kwargs)
        return wrapper
    return decorator if func is None else decorator(func)
