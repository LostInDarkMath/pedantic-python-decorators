from functools import wraps
from typing import Callable

from pedantic.constants import F, ReturnType


class Rename:
    def __init__(self, from_: str, to: str) -> None:
        self.from_ = from_
        self.to = to


def rename_kwargs(*params: Rename) -> Callable[[F], F]:
    """
        Renames the keyword arguments based on the given "Rename" rules when the decorated function is called.
        You can also use this to define aliases for keyword arguments.

        Example:

        >>> @rename_kwargs(
        ...     Rename(from_='firstname', to='a'),
        ...     Rename(from_='lastname', to='b'),
        ... )
        ... def my_function(a, b):
        ...     return a + ' ' + b
        >>> my_function(a='egon', b='olsen')  # the normal way
        'egon olsen'
        >>> my_function(firstname='egon', lastname='olsen')  # using new defined keyword arguments
        'egon olsen'
    """

    param_dict = {p.from_: p.to for p in params}

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs) -> ReturnType:
            result_kwargs = {}

            for k, v in kwargs.items():
                if k in param_dict:
                    result_kwargs[param_dict[k]] = kwargs[k]
                else:
                    result_kwargs[k] = kwargs[k]

            return func(*args, **result_kwargs)
        return wrapper
    return decorator


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
