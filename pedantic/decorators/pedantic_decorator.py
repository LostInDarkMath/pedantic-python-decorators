import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar, overload

from pedantic.decorators.helpers import add_type_var_attr_and_method_to_class, decorate_class
from pedantic.get_context import get_context
from pedantic.models.decorated_function import DecoratedFunction
from pedantic.models.function_call import FunctionCall
from pedantic.type_checking_logic.check_docstring import check_docstring

P = ParamSpec('P')
R = TypeVar('R')
T = TypeVar('T', bound=type)

@overload
def pedantic(func: Callable[P, R]) -> Callable[P, R]: ...


@overload
def pedantic(cls: T) -> T: ...


@overload
def pedantic(
    *,
    require_docstring: bool = False,
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


@overload
def pedantic(
    *,
    require_docstring: bool = False,
) -> Callable[[T], T]: ...


def pedantic(
    func: Callable[P, R] | type | None = None,
    *,
    require_docstring: bool = False,
) -> Any:
    """
     A PedanticException is raised if one of the following happened:
     - The decorated function is called with positional arguments.
     - The function has no type annotation for their return type or one or more parameters do not have type
         annotations.
     - A type annotation is incorrect.
     - A type annotation misses type arguments, e.g. typing.List instead of typing.List[int].
     - The documented arguments do not match the argument list or their type annotations.

     You can use this as a function or a class decorator.

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

    def decorator(f: Callable[P, R] | type) -> Callable[P, R]:
        if inspect.isclass(f):
            add_type_var_attr_and_method_to_class(f)
            return decorate_class(
                cls=f,
                decorate_callable=_decorate_callable,
                allowed_dunder_methods=['__init__', '__contains__'],
            )

        return _decorate_callable(f)

    def _decorate_callable(f: Callable[P, R]) -> Callable[P, R]:
        decorated_func = DecoratedFunction(func=f)

        if decorated_func.docstring is not None and (require_docstring or len(decorated_func.docstring.params)) > 0:
            check_docstring(decorated_func=decorated_func)

        if decorated_func.is_coroutine:
            async def async_wrapper(*args: Any, **kwargs: Any) -> R:
                call = FunctionCall(func=decorated_func, args=args, kwargs=kwargs, context=get_context(2))
                call.assert_uses_kwargs()
                return await call.async_check_types()

            return async_wrapper

        @wraps(f)
        def sync_wrapper(*args: Any, **kwargs: Any) -> R:
            call = FunctionCall(func=decorated_func, args=args, kwargs=kwargs, context=get_context(2))
            call.assert_uses_kwargs()
            return call.check_types()

        return sync_wrapper

    return decorator if func is None else decorator(f=func)
