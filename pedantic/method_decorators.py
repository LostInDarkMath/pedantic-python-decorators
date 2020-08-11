import functools
import inspect
from typing import Callable, Any, Tuple, Dict, Type, Optional
from datetime import datetime
from docstring_parser import parse, Docstring
import warnings

# local file imports
from pedantic.custom_exceptions import NotImplementedException, TooDirtyException
from pedantic.type_hint_parser import is_instance


# HELPER FUNCTIONS ###
def __is_instance_method(func: Callable) -> bool:
    spec = inspect.getfullargspec(func)
    return spec.args and spec.args[0] == 'self'


def __get_args_without_self(func: Callable, args: Tuple[Any, ...]) -> Tuple[Any, ...]:
    return args[1:] if __is_instance_method(func) else args  # self is always the first argument if present


def __require_kwargs(func: Callable, args: Tuple[Any, ...]) -> None:
    args_without_self = __get_args_without_self(func=func, args=args)
    assert args_without_self == (), f'Use kwargs when you call {func.__name__}! {args_without_self}'


def __is_value_matching_type_hint(value: Any, type_hint: Any) -> bool:
    if type_hint is None:
        return value == type_hint
    return is_instance(value, type_hint)


def __get_parsed_docstring(func: Callable) -> Docstring:
    docstring = func.__doc__.strip() if func.__doc__ is not None else ''
    return parse(docstring)


def __get_annotations(func: Callable) -> Dict[str, Any]:
    return inspect.getfullargspec(func).annotations


def __require_kwargs_and_type_checking(func: Callable,
                                       args: Tuple[Any, ...],
                                       kwargs: Dict[str, Any],
                                       annotations: Dict[str, Any]) -> Any:
    """ Passing annotations here has the advantage, that it only needs be calculated once
    and not during every function call.
    """

    __require_kwargs(func=func, args=args)
    assert len(kwargs) + 1 == len(annotations), \
        f'Function "{func.__name__}" misses some type hints or arguments: {kwargs}, {annotations}'

    for kwarg in kwargs:
        expected_type = annotations[kwarg]
        assert __is_value_matching_type_hint(value=kwargs[kwarg], type_hint=expected_type), \
            f'Argument {kwarg}={kwargs[kwarg]} has not type {expected_type}.'

    result = func(*args, **kwargs)
    expected_result_type = annotations['return']

    if isinstance(expected_result_type, str):
        assert result.__class__.__name__ == expected_result_type, f'Do not use strings as type hints!'
    else:
        assert __is_value_matching_type_hint(value=result, type_hint=expected_result_type), \
            f'Return type of function "{func.__name__}" is wrong: ' \
            f'Expected {expected_result_type}, but got {type(result)}.'
    return result


def __require_docstring_google_format(func: Callable, docstring: Docstring, annotations: Dict[str, Any]) -> None:
    """
        Of course, the params docstring and annotations are absolute here, but passing saves performance here,
        because they are only calculated once. If we would calculate them here, it would be very expensive.
    """

    num_documented_args = len(docstring.params)
    num_taken_args = len([a for a in annotations if a != 'return'])
    assert num_documented_args == num_taken_args, \
        f'There are {num_documented_args} argument(s) documented, but ' \
        f'{num_taken_args} are actually taken by function "{func.__name__}".'

    assert (docstring.returns is None) == ('return' not in annotations or annotations['return'] is None), \
        f'The documented return type "{docstring.returns}" does not match the annotated return type.'

    for annotation in annotations:
        expected_type_raw = annotations[annotation]
        if 'typing.' in str(expected_type_raw):
            expected_type = str(annotations[annotation]).replace('typing.', '')
        elif hasattr(expected_type_raw, '__name__'):
            expected_type = expected_type_raw.__name__
        elif isinstance(expected_type_raw, str):
            expected_type = expected_type_raw
        else:
            expected_type = None

        if annotation == 'return' and annotations[annotation] is not None:
            assert docstring.returns is not None, \
                f'Function "{func.__name__}" returns type "{annotations[annotation]}", ' \
                f'but there is no return value documented.'
            assert docstring.returns.args[0] == 'returns', f"That's weird."
            assert len(docstring.returns.args) == 2, \
                f'Parse Error: Only docstrings in the Google format are supported.'

            actual_return_type: str = docstring.returns.args[1]
            assert actual_return_type == expected_type, \
                f'Type does not match: Type annotation expect "{expected_type}" ' \
                f'but type "{actual_return_type}" was documented.'
        elif annotation != 'return':  # parameters passed to function
            docstring_param = None
            for param in docstring.params:
                if param.arg_name == annotation:
                    docstring_param = param
            if docstring_param is None:
                raise AssertionError(f'Parameter "{annotation}" is not documented!')

            assert expected_type == docstring_param.type_name, \
                f'Type of parameter "{annotation}" does not match: it has type "{expected_type}", ' \
                f'but type "{docstring_param.type_name}" is documented instead!'


def __raise_warning(msg: str, category: Type[Warning]):
    warnings.simplefilter('always', category)  # turn off filter
    warnings.warn(msg, category=category, stacklevel=2)
    warnings.simplefilter('default', category)  # reset filter


# DECORATORS ###
def overrides(interface_class: Any) -> Callable:
    """
        Example:
        >>> class Parent:
        >>>     def instance_method(self):
        >>>         pass
        >>> class Child(Parent):
        >>>     @overrides(Parent)
        >>>     def instance_method(self):
        >>>         print('hi')
    """
    def overrider(func: Callable) -> Callable:
        assert __is_instance_method(func), f'Function "{func.__name__}" is not an instance method!'
        assert (func.__name__ in dir(interface_class)), \
            f"Parent class {interface_class.__name__} does not have such a method '{func.__name__}'."
        return func
    return overrider


def timer(func: Callable) -> Callable:
    """
        Prints out how long the execution of the function takes in seconds.
        Example:
        >>> @timer
        >>> def some_calculation():
        >>>     return 42
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time: datetime = datetime.now()
        value: Any = func(*args, **kwargs)
        end_time = datetime.now()
        run_time = end_time - start_time
        print("Timer: Finished function {} in {}.".format(repr(func.__name__), run_time))
        return value
    return wrapper


def count_calls(func: Callable) -> Callable:
    """
        Prints how often the method is called during program execution.
        Example:
        >>> @count_calls
        >>> def some_calculation():
        >>>     return 42
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        wrapper.num_calls += 1
        print(f"Count Calls: Call {wrapper.num_calls} of function {func.__name__!r} at {datetime.now()}.")
        return func(*args, **kwargs)

    wrapper.num_calls = 0
    return wrapper


def trace(func: Callable) -> Callable:
    """
       Prints the passed arguments and keyword arguments and return values on each function call.
       Example:
       >>> @trace
       >>> def some_calculation(a, b, c):
       >>>     return a + b + c
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        print(f'Trace: {datetime.now()} calling {func.__name__}()  with {args}, {kwargs}')
        original_result = func(*args, **kwargs)
        print(f'Trace: {datetime.now()} {func.__name__}() returned {original_result!r}')
        return original_result
    return wrapper


def deprecated(func: Callable) -> Callable:
    """This is a decorator which can be used to mark functions as deprecated. It will result in a warning being emitted
    when the function is used."""
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        __raise_warning(msg="Call to deprecated function {}.".format(func.__name__), category=DeprecationWarning)
        return func(*args, **kwargs)
    return new_func


def needs_refactoring(func: Callable) -> Callable:
    """
        Of course, you refactor immediately if you see something ugly.
        However, if you don't have the time for a big refactoring use this decorator at least.
        A warning is printed everytime the decorated function is called.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        __raise_warning(msg=f'Function "{func.__name__}" looks terrible and needs a refactoring!', category=UserWarning)
        return func(*args, **kwargs)
    return wrapper


def unimplemented(func: Callable) -> Callable:
    """
        For documentation purposes. Throw NotImplementedException if the function is called.
        Example:
        >>> @unimplemented
        >>> def some_calculation(a, b, c):
        >>>     pass
        >>> some_calculation(5, 4, 3)       # this will lead to an NotImplementedException
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        raise NotImplementedException(f'Function "{func.__name__}" is not implemented yet!')
    return wrapper


def dirty(func: Callable) -> Callable:
    """
        Prevents dirty code from beeing executed.
        Example:
        >>> @dirty
        >>> def some_calculation(a, b, c):
        >>>     return a + a + a + a + a
        >>> some_calculation(5, 4, 3)       # this will lead to an TooDirtyException
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        raise TooDirtyException(f'Function "{func.__name__}" is too dirty to be executed!')
    return wrapper


def require_kwargs(func: Callable) -> Callable:
    """
        Checks that each passed argument is a keyword argument.
        Example:
        >>> @require_kwargs
        >>> def some_calculation(a, b, c):
        >>>     return a + b + c
        >>> some_calculation(5, 4, 3)       # this will lead to an AssertionError
        >>> some_calculation(a=5, b=4, c=3) # this is okay
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        __require_kwargs(func=func, args=args)
        return func(*args, **kwargs)
    return wrapper


def validate_args(validator: Callable[[Any], Tuple[bool, str]]) -> Callable:
    """
      Validates each passed argument with the given validator.
      Example:
      >>> @validate_args(lambda x: (x > 42, f'Each argument should be greater then 42, but it was {x}.'))
      >>> def some_calculation(a, b, c):
      >>>     return a + b + c
      >>> some_calculation(30, 40, 50)  # this leads to an error
      >>> some_calculation(43, 40, 50)  # this is okay
   """
    def outer(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            args_without_self = __get_args_without_self(func=func, args=args)

            for arg in args_without_self:
                res, msg = validator(arg)
                assert res, msg

            for kwarg in kwargs:
                res, msg = validator(kwargs[kwarg])
                assert res, msg
            return func(*args, **kwargs)
        return wrapper
    return outer


def require_not_none(func: Callable) -> Callable:
    """
      Checks that each passed argument is not None and raises AssertionError if there is some.
      Example:
      >>> @require_not_none
      >>> def some_calculation(a, b, c):
      >>>     return a + b + c
   """
    def validator(arg: Any) -> Tuple[bool, str]:
        return arg is not None, f'Argument of function "{func.__name__}" should not be None!'
    return validate_args(validator)(func)


def require_not_empty_strings(func: Callable) -> Callable:
    """
       Throw a ValueError if the arguments are None, not strings, or empty strings or contains only whitespaces.
       Example:
       >>> @require_not_empty_strings
       >>> def some_calculation(a, b, c):
       >>>     print(a, b, c)
       >>> some_calculation('Hi', '   ', 'you')    # this will lead to an ValueError
       >>> some_calculation('Hi', None, 'you')     # this will lead to an ValueError
       >>> some_calculation('Hi', 42, 'you')       # this will lead to an ValueError
   """
    def validator(arg: Any) -> Tuple[bool, str]:
        return arg is not None and type(arg) is str and len(arg.strip()) > 0, \
            f'Arguments of function "{func.__name__}" should be a not empty string! Got: {arg}'
    return validate_args(validator)(func)


def pedantic(func: Callable) -> Callable:
    """
       Checks the types and throw an AssertionError if a type is incorrect.
       This decorator reads the type hints and use them as contracts that will be checked.
       If the function misses type hints, it will raise an AssertionError.
       It also forces the usage of keyword arguments. Otherwise, type checking would be impossible.

       Example:
       >>> @pedantic
       >>> def some_calculation(a: int, b: float, c: str) -> bool:
       >>>     print(a, b, c)
       >>>     return float(a) == b
       >>> some_calculation(a=42.0, b=14.0, c='you')   # this will lead to an AssertionError
       >>> some_calculation(a=42, b=None, c='you')     # this will lead to an AssertionError
       >>> some_calculation(a=42, b=42, c='you')       # this will lead to an AssertionError
       >>> some_calculation(5, 4.0, 'hi')              # this will lead to an AssertionError
   """

    annotations = __get_annotations(func=func)
    docstring = __get_parsed_docstring(func=func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        if len(__get_parsed_docstring(func=func).params) > 0:
            __require_docstring_google_format(func=func, annotations=annotations, docstring=docstring)
        return __require_kwargs_and_type_checking(func=func, args=args, kwargs=kwargs, annotations=annotations)
    return wrapper


def pedantic_require_docstring(func: Callable) -> Callable:
    """It's like pedantic, but now it forces you to write docstrings (Google format)."""

    annotations = __get_annotations(func=func)
    docstring = __get_parsed_docstring(func=func)

    def wrapper(*args, **kwargs) -> Any:
        __require_docstring_google_format(func=func, annotations=annotations, docstring=docstring)
        res = __require_kwargs_and_type_checking(func=func, args=args, kwargs=kwargs, annotations=annotations)
        return res
    return wrapper
