from collections.abc import Callable
from typing import TypeVar

from pedantic.exceptions import PedanticOverrideException

F = TypeVar('F', bound=Callable)


def overrides(base_class: type) -> F:
    """
    Use this to mark methods which overrides methods of a parent class.

    Raises:
        PedanticOverrideException: if the decorated method is not a method in any parent class

    Example:
    >>> class Parent:
    ...     def my_instance_method(self): pass
    >>> class Child(Parent):
    ...     @overrides(Parent)
    ...     def my_instance_method(self): pass
    """

    def decorator(func: F) -> F:
        func_name = func.__name__

        if func_name not in dir(base_class):
            raise PedanticOverrideException(
                f'In function {func.__qualname__}:\n '
                f'Base class "{base_class.__name__}" does not have such a method "{func_name}".')
        return func
    return decorator
