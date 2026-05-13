import inspect
from collections.abc import Callable
from datetime import UTC, datetime
from functools import wraps
from typing import Any, ParamSpec, TypeVar, overload

from pedantic.decorators.helpers import decorate_class

P = ParamSpec('P')
R = TypeVar('R')
T = TypeVar('T', bound=type)


@overload
def trace(func: Callable[P, R]) -> Callable[P, R]: ...


@overload
def trace(cls: T) -> T: ...


@overload
def trace(
    *,
    log: Callable[[str], None] = print,
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


@overload
def trace(
    *,
    log: Callable[[str], None] = print,
) -> Callable[[T], T]: ...


def trace(
    obj: Callable[P, R] | type | None = None,
    *,
    log: Callable[[str], None] = print,
) -> Any:
    """
    Decorate a function or class to trace calls, arguments, and return values.

    Can be used as:

        @trace
        def foo(...): ...

        @trace(log=print)
        async def foo(...): ...

        @trace
        class Foo: ...

        @trace(log=logger.info)
        class Foo: ...

    Supports:
        - synchronous functions
        - asynchronous functions
        - classes
        - instance methods
        - static methods
        - class methods

    Args:
        obj:
            The decorated object when used as ``@trace``.

        log:
            Callable used to emit trace messages.

    Returns:
        The wrapped function, class, or decorator.
    """

    def decorator(obj_: Any) -> Any:
        if inspect.isclass(obj_):
            return decorate_class(obj_, _decorate_callable, log)

        return _decorate_callable(obj_, log)

    if obj is not None:
        return decorator(obj)

    return decorator


def _decorate_callable(
    func: Callable[P, R],
    log: Callable[[str], None],
) -> Callable[P, R]:
    func_name = func.__qualname__

    def _log_before_call(args: tuple[Any, ...], kwargs: dict[str, Any]) -> None:
        log(f'Trace: {_get_now()} calling {func_name}() with {args}, {kwargs}')

    def _log_after_call(result: Any) -> None:
        log(f'Trace: {_get_now()} {func_name}() returned {result!r}')

    if inspect.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            _log_before_call(args, kwargs)
            result = await func(*args, **kwargs)
            _log_after_call(result)
            return result

        return async_wrapper

    @wraps(func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        _log_before_call(args, kwargs)
        result = func(*args, **kwargs)
        _log_after_call(result)
        return result

    return sync_wrapper


def _get_now() -> datetime:
    return datetime.now(tz=UTC)
