import inspect
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

P = ParamSpec('P')
R = TypeVar('R')
T = TypeVar('T', bound=type)


def decorate_class(cls: T, _decorate_callable: Callable[[Callable, ...], Callable], *args: Any) -> T:
    """Applies a decorator with optional arguments to each method of a class."""

    for attr_name, attr_value in vars(cls).items():
        if attr_name.startswith('__') and attr_name.endswith('__'):
            continue

        if inspect.isfunction(attr_value) or inspect.ismethod(attr_value):
            setattr(cls, attr_name, _decorate_callable(attr_value, *args))

        elif isinstance(attr_value, staticmethod):
            wrapped = _decorate_callable(attr_value.__func__, *args)
            setattr(cls, attr_name, staticmethod(wrapped))

        elif isinstance(attr_value, classmethod):
            wrapped = _decorate_callable(attr_value.__func__, *args)
            setattr(cls, attr_name, classmethod(wrapped))

    return cls
