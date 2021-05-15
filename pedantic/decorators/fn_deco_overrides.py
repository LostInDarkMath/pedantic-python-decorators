from typing import Type

from pedantic.constants import F
from pedantic.exceptions import PedanticOverrideException
from pedantic.models.decorated_function import DecoratedFunction


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
        deco_func = DecoratedFunction(func=func)
        uses_multiple_decorators = deco_func.num_of_decorators > 1

        if not deco_func.is_instance_method and not uses_multiple_decorators:
            raise PedanticOverrideException(
                f'{deco_func.err} Function "{deco_func.name}" should be an instance method of a class!')

        if deco_func.name not in dir(base_class):
            raise PedanticOverrideException(
                f'{deco_func.err} Base class "{base_class.__name__}" does not have such a method "{deco_func.name}".')
        return func
    return decorator


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
