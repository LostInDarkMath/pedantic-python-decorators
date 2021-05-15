from functools import wraps
from typing import Callable, Any, Union, Tuple

from pedantic.constants import F, ReturnType
from pedantic.models.decorated_function import DecoratedFunction
from pedantic.models.function_call import FunctionCall


def validate_args(validator: Callable[[Any], Union[bool, Tuple[bool, str]]]) -> F:
    """
      Validates each passed argument with the given validator.

      Example:

      >>> @validate_args(lambda x: (x > 42, f'Each argument should be greater then 42, but it was {x}.'))
      ... def my_function(a, b, c):
      ...     return a + b + c
      >>> my_function(80, 40, 50)
      Traceback (most recent call last):
      ...
      AssertionError: In function my_function:
      Each argument should be greater then 42, but it was 40.
      >>> my_function(43, 48, 50)
      141
   """

    def outer(func: F) -> F:
        deco_func = DecoratedFunction(func=func)

        def validate(obj: Any) -> None:
            res = validator(obj)
            res, msg = res if type(res) is not bool else (res, 'Invalid arguments.')
            if not res:
                raise AssertionError(f'{deco_func.err}{msg}')

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            call = FunctionCall(func=DecoratedFunction(func=func), args=args, kwargs=kwargs)

            for arg in call.args_without_self:
                validate(arg)

            for kwarg in kwargs:
                validate(kwargs[kwarg])

            return func(*args, **kwargs)
        return wrapper
    return outer


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
