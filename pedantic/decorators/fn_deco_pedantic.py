from functools import wraps
from typing import Any, Optional

from pedantic.type_checking_logic.check_docstring import _check_docstring
from pedantic.constants import ReturnType, F
from pedantic.models.decorated_function import DecoratedFunction
from pedantic.models.function_call import FunctionCall
from pedantic.env_var_logic import is_enabled


def pedantic(func: Optional[F] = None, require_docstring: bool = False) -> F:
    """
        A PedanticException is raised if one of the following happened:
        - The decorated function is called with positional arguments.
        - The function has no type annotation for their return type or one or more parameters do not have type
            annotations.
        - A type annotation is incorrect.
        - A type annotation misses type arguments, e.g. typing.List instead of typing.List[int].
        - The documented arguments do not match the argument list or their type annotations.

       Example:

       >>> @pedantic
       ... def my_function(a: int, b: float, c: str) -> bool:
       ...     return float(a) == b and str(b) == c
       >>> my_function(a=42.0, b=14.0, c='hi')
       Traceback (most recent call last):
       ...
       pedantic.exceptions.PedanticTypeCheckException: In function my_function:
       Type hint is incorrect: Argument a=42.0 of type <class 'float'> does not match expected type <class 'int'>.
       >>> my_function(a=42, b=None, c='hi')
       Traceback (most recent call last):
       ...
       pedantic.exceptions.PedanticTypeCheckException: In function my_function:
       Type hint is incorrect: Argument b=None of type <class 'NoneType'> does not match expected type <class 'float'>.
       >>> my_function(a=42, b=42, c='hi')
       Traceback (most recent call last):
       ...
       pedantic.exceptions.PedanticTypeCheckException: In function my_function:
       Type hint is incorrect: Argument b=42 of type <class 'int'> does not match expected type <class 'float'>.
       >>> my_function(5, 4.0, 'hi')
       Traceback (most recent call last):
       ...
       pedantic.exceptions.PedanticCallWithArgsException: In function my_function:
       Use kwargs when you call function my_function. Args: (5, 4.0, 'hi')
   """

    def decorator(f: F) -> F:
        if not is_enabled():
            return f

        decorated_func = DecoratedFunction(func=f)

        if require_docstring or len(decorated_func.docstring.params) > 0:
            _check_docstring(decorated_func=decorated_func)

        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            call = FunctionCall(func=decorated_func, args=args, kwargs=kwargs)
            call.assert_uses_kwargs()
            return call.check_types()

        async def async_wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            call = FunctionCall(func=decorated_func, args=args, kwargs=kwargs)
            call.assert_uses_kwargs()
            return await call.async_check_types()

        if decorated_func.is_coroutine:
            return async_wrapper
        else:
            return wrapper

    return decorator if func is None else decorator(f=func)


def pedantic_require_docstring(func: Optional[F] = None) -> F:
    """Shortcut for @pedantic(require_docstring=True) """
    return pedantic(func=func, require_docstring=True)


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
