from functools import wraps
from typing import Any

from pedantic.constants import F, ReturnType
from pedantic.models.decorated_function import DecoratedFunction
from pedantic.models.function_call import FunctionCall


def require_kwargs(func: F) -> F:
    """
        Checks that each passed argument is a keyword argument.

        Example:

        >>> @require_kwargs
        ... def my_function(a, b, c):
        ...     return a + b + c
        >>> my_function(5, 4, 3)
        Traceback (most recent call last):
        ...
        pedantic.exceptions.PedanticCallWithArgsException: In function my_function:
        Use kwargs when you call function my_function. Args: (5, 4, 3)
        >>> my_function(a=5, b=4, c=3)
        12
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
        decorated_func = DecoratedFunction(func=func)
        call = FunctionCall(func=decorated_func, args=args, kwargs=kwargs)
        call.assert_uses_kwargs()
        return func(*args, **kwargs)
    return wrapper


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
