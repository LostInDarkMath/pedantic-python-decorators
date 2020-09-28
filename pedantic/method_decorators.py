import functools
from typing import Callable, Any, Tuple, Type, Union, Optional
from datetime import datetime
import warnings

from pedantic.check_docstring import _check_docstring
from pedantic.models.function_call import FunctionCall
from pedantic.set_envionment_variables import is_enabled
from pedantic.constants import ReturnType, F
from pedantic.exceptions import NotImplementedException, TooDirtyException, PedanticOverrideException
from pedantic.models.decorated_function import DecoratedFunction


def overrides(base_class: Any) -> F:
    """
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


def timer(func: F) -> F:
    """
        Prints how long the execution of the decorated function takes.
        Example:
        >>> @timer
        ... def long_taking_calculation():
        ...     return 42
        >>> long_taking_calculation()
        Timer: Finished function "long_taking_calculation" in 0:00:00...
        42
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
        start_time: datetime = datetime.now()
        value = func(*args, **kwargs)
        end_time = datetime.now()
        run_time = end_time - start_time
        print(f'Timer: Finished function "{func.__name__}" in {run_time}.')
        return value
    return wrapper


def count_calls(func: F) -> F:
    """
        Prints how often the method is called during program execution.
        Example:
        >>> @count_calls
        ... def often_used_method():
        ...    return 42
        >>> often_used_method()
        Count Calls: Call 1 of function 'often_used_method' at ...
        >>> often_used_method()
        Count Calls: Call 2 of function 'often_used_method' at ...
        >>> often_used_method()
        Count Calls: Call 3 of function 'often_used_method' at ...
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
        wrapper.num_calls += 1
        print(f"Count Calls: Call {wrapper.num_calls} of function {func.__name__!r} at {datetime.now()}.")
        return func(*args, **kwargs)

    wrapper.num_calls = 0
    return wrapper


def trace(func: F) -> F:
    """
       Prints the passed arguments and the returned value on each function call.
       Example:
       >>> @trace
       ... def my_function(a, b, c):
       ...     return a + b + c
       >>> my_function(4, 5, 6)
       Trace: ... calling my_function()  with (4, 5, 6), {}
       Trace: ... my_function() returned 15
       15
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
        print(f'Trace: {datetime.now()} calling {func.__name__}()  with {args}, {kwargs}')
        original_result = func(*args, **kwargs)
        print(f'Trace: {datetime.now()} {func.__name__}() returned {original_result!r}')
        return original_result
    return wrapper


def trace_if_returns(return_value: ReturnType) -> F:
    """
       Prints the passed arguments if and only if the decorated function returned the given return_value.
       This is useful if you want to figure out which input arguments leads to a special return value.
       Example:
       >>> @trace_if_returns(42)
       ... def my_function(a, b, c):
       ...     return a + b + c
       >>> my_function(1, 2, 3)
       6
       >>> my_function(10, 8, 24)
       Function my_function returned value 42 for args: (10, 8, 24) and kwargs: {}
       42
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            result = func(*args, **kwargs)
            if result == return_value:
                print(f'Function {func.__name__} returned value {result} for args: {args} and kwargs: {kwargs}')
            return result
        return wrapper
    return decorator


def does_same_as_function(other_func: F) -> F:
    """
        Each time the decorated function is executed, the function other_func is also executed and the results
        are compared. An AssertionError is raised if the results are not equal.
        Example:
        >>> def other_calculation(a, b, c):
        ...     return c + b + a
        >>> @does_same_as_function(other_calculation)
        ... def some_calculation(a, b, c):
        ...     return a + b + c
        >>> some_calculation(1, 2, 3)
        6
    """

    def decorator(decorated_func: F) -> F:
        @functools.wraps(decorated_func)
        def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            result = decorated_func(*args, **kwargs)
            other = other_func(*args, **kwargs)

            if other != result:
                raise AssertionError(f'Different outputs: Function "{decorated_func.__name__}" returns {result} and '
                                     f'function "{other_func.__name__}" returns {other} for parameters {args} {kwargs}')
            return result
        return wrapper
    return decorator


def deprecated(func: F) -> F:
    """
        Use this decorator to mark a function as deprecated. It will raise a warning when the function is called.
        Example:
        >>> @deprecated
        ... def my_function(a, b, c):
        ...     pass
        >>> my_function(5, 4, 3)
    """

    @functools.wraps(func)
    def new_func(*args: Any, **kwargs: Any) -> ReturnType:
        _raise_warning(msg=f'Call to deprecated function {func.__qualname__}.', category=DeprecationWarning)
        return func(*args, **kwargs)
    return new_func


def needs_refactoring(func: F) -> F:
    """
        Of course, you refactor immediately if you see something ugly.
        However, if you don't have the time for a big refactoring use this decorator at least.
        A warning is printed everytime the decorated function is called.
        Example:
        >>> @needs_refactoring
        ... def my_function(a, b, c):
        ...     pass
        >>> my_function(5, 4, 3)
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
        _raise_warning(msg=f'Function {func.__qualname__} looks terrible and needs a refactoring!',
                       category=UserWarning)
        return func(*args, **kwargs)
    return wrapper


def unimplemented(func: F) -> F:
    """
        For documentation purposes. Throw NotImplementedException if the function is called.
        Example:
        >>> @unimplemented
        ... def my_function(a, b, c):
        ...     pass
        >>> my_function(5, 4, 3)
        Traceback (most recent call last):
        ...
        pedantic.exceptions.NotImplementedException: Function "my_function" is not implemented yet!
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
        raise NotImplementedException(f'Function "{func.__qualname__}" is not implemented yet!')
    return wrapper


def dirty(func: F) -> F:
    """
        Prevents dirty code from beeing executed.
        Example:
        >>> @dirty
        ... def my_function(a, b, c):
        ...     return a + a + a + a + a
        >>> my_function(5, 4, 3)
        Traceback (most recent call last):
        ...
        pedantic.exceptions.TooDirtyException: Function "my_function" is too dirty to be executed!
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
        raise TooDirtyException(f'Function "{func.__qualname__}" is too dirty to be executed!')
    return wrapper


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

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
        decorated_func = DecoratedFunction(func=func)
        call = FunctionCall(func=decorated_func, args=args, kwargs=kwargs)
        call.assert_uses_kwargs()
        return func(*args, **kwargs)
    return wrapper


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

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            call = FunctionCall(func=DecoratedFunction(func=func), args=args, kwargs=kwargs)

            for arg in call.args_without_self:
                validate(arg)

            for kwarg in kwargs:
                validate(kwargs[kwarg])

            return func(*args, **kwargs)
        return wrapper
    return outer


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

        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            call = FunctionCall(func=decorated_func, args=args, kwargs=kwargs)
            call.assert_uses_kwargs()
            return call.check_types()
        return wrapper
    return decorator if func is None else decorator(f=func)


def pedantic_require_docstring(func: Optional[F] = None) -> F:
    """Shortcut for @pedantic(require_docstring=True) """
    return pedantic(func=func, require_docstring=True)


def _raise_warning(msg: str, category: Type[Warning]) -> None:
    warnings.simplefilter(action='always', category=category)
    warnings.warn(message=msg, category=category, stacklevel=2)
    warnings.simplefilter(action='default', category=category)


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
