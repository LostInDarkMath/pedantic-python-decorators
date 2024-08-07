from typing import Type

from pedantic.constants import F
from pedantic.exceptions import PedanticOverrideException


def overrides(base_class: Type) -> F:
    """
        This is used for marking methods that overrides methods of the base class which makes the code more readable.
        This decorator raises an Exception if the decorated method is not a method in the parent class.

        Example:

        >>> class Parent:
        ...     def my_instance_method(self):
        ...         pass
        >>> class Child(Parent):
        ...     @overrides(Parent)
        ...     def my_instance_method(self):
        ...         print('hello world')
    """

    def decorator(func: F) -> F:
        name = func.__name__

        if name not in dir(base_class):
            raise PedanticOverrideException(
                f'In function {func.__qualname__}:\n '
                f'Base class "{base_class.__name__}" does not have such a method "{name}".')
        return func
    return decorator


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
