import functools
import inspect
from typing import Callable, Any, Tuple, Dict, Type, Union
from datetime import datetime
import warnings
import re

# third party
from docstring_parser import parse, Docstring

# local file imports
from pedantic.custom_exceptions import NotImplementedException, TooDirtyException
from pedantic.type_hint_parser import is_instance


# HELPER FUNCTIONS ###
def __is_instance_method(func: Callable) -> bool:
    spec = inspect.getfullargspec(func)
    return spec.args and spec.args[0] == 'self'


def __is_static_method(func: Callable[..., Any]) -> bool:
    return '@staticmethod' in inspect.getsource(func)


def __is_property_setter(func: Callable[..., Any]) -> bool:
    return f'@{func.__name__}.setter' in inspect.getsource(func)


def __uses_multiple_decorators(func: Callable[..., Any], max_allowed: int = 1) -> bool:
    return len(re.findall('@', inspect.getsource(func).split('def')[0])) > max_allowed


def __get_args_without_self(func: Callable, args: Tuple[Any, ...], max_allowed) -> Tuple[Any, ...]:
    if __is_instance_method(func) or __is_static_method(func) or __uses_multiple_decorators(func, max_allowed):
        return args[1:]  # self is always the first argument if present
    return args


def __require_kwargs(func: Callable, args: Tuple[Any, ...], max_allowed: int) -> None:
    args_without_self = __get_args_without_self(func=func, args=args, max_allowed=max_allowed)

    if __is_special_func(func=func) or __is_property_setter(func=func):
        return

    assert args_without_self == (), f'{__qual_name(func=func)} Use kwargs when you call function {func.__name__}. ' \
                                    f'Args: {args_without_self}'


def __is_special_func(func: Callable[..., Any]) -> bool:
    name = func.__name__
    if not name.startswith('__') or not name.endswith('__'):
        return False
    return name not in [f'__{s}__' for s in ['new', 'init', 'str', 'del', 'int', 'float', 'complex', 'oct', 'hex',
                                             'index', 'trunc', 'repr', 'unicode', 'hash', 'nonzero', 'dir', 'sizeof']]


def __qual_name(func: Callable[..., Any]) -> str:
    """uniform design for error messages"""
    return f'In function {func.__qualname__}:' + '\n'


def __is_value_matching_type_hint(value: Any, type_hint: Any, func: Callable[..., Any]) -> bool:
    """Wrapper for file "type_hint_parser.py"."""

    if type_hint is None:
        return value == type_hint
    assert type(type_hint) is not tuple, \
        f'{__qual_name(func=func)} Use "Tuple[]" instead of "{type_hint}" as type hint.'
    assert type_hint is not tuple, f'{__qual_name(func=func)} Use "Tuple[]" instead of "tuple" as type hint.'
    assert type_hint is not list, f'{__qual_name(func=func)} Use "List[]" instead of "list" as type hint.'
    assert type_hint is not dict, f'{__qual_name(func=func)} Use "Dict[]" instead of "dict" as type hint.'
    assert type_hint is not set, f'{__qual_name(func=func)} Use "Set[]" instead of "set" as type hint.'
    assert type_hint is not frozenset, \
        f'{__qual_name(func=func)} Use "FrozenSet[]" instead of "frozenset" as type hint.'

    try:
        return is_instance(value, type_hint)
    except AssertionError as ex:
        raise AssertionError(f'{__qual_name(func=func)} {ex}')
    except (AttributeError, Exception) as ex:
        raise AssertionError(f'{__qual_name(func=func)} An error occurred during type hint checking. '
                             f'Value: {value} Annotation: {type_hint} '
                             f'Mostly this is caused by an incorrect type annotation. '
                             f'Details: {ex} ')


def __get_parsed_docstring(func: Callable) -> Docstring:
    docstring = func.__doc__.strip() if func.__doc__ is not None else ''
    try:
        return parse(docstring)
    except (Exception, TypeError) as ex:
        raise AssertionError(f'{__qual_name(func=func)} Could not parse docstring. Please check syntax. Details: {ex}')


def __get_annotations(func: Callable) -> Dict[str, Any]:
    return inspect.getfullargspec(func).annotations


def __require_kwargs_and_type_checking(func: Callable,
                                       args: Tuple[Any, ...],
                                       kwargs: Dict[str, Any],
                                       annotations: Dict[str, Any],
                                       signature: inspect.Signature,
                                       max_allowed: int) -> Any:
    """ Passing annotations and signature here has the advantage, that it only needs be calculated once
    and not during every function call.
    """
    __require_kwargs(func=func, args=args, max_allowed=max_allowed)
    params = signature.parameters

    assert signature.return_annotation is not inspect.Signature.empty, \
        f'{__qual_name(func=func)} Their should be a type hint for the return type ' \
        f'(e.g. None if there is nothing returned).'

    i = 1 if __is_instance_method(func=func) else 0
    for key in params:
        param = params[key]
        expected_type = param.annotation

        if param.name == 'self':
            continue

        assert expected_type is not inspect.Signature.empty, \
            f'{__qual_name(func=func)} Parameter "{param.name}" should have a type hint.'

        if param.default is inspect.Signature.empty:
            if __is_special_func(func=func) or __is_property_setter(func=func):
                actual_value = args[i]
                i += 1
            else:
                assert key in kwargs, f'{__qual_name(func=func)} Parameter "{key}" is unfilled.'
                actual_value = kwargs[key]
        else:
            actual_value = kwargs[key] if key in kwargs else param.default

        if isinstance(expected_type, str):
            class_name = actual_value.__class__.__name__
            assert class_name == expected_type, \
                f'{__qual_name(func=func)} Type hint is incorrect. Expected: {expected_type} but was {class_name} instead.'
        else:
            assert __is_value_matching_type_hint(value=actual_value, type_hint=expected_type, func=func), \
                f'{__qual_name(func=func)} Type hint is incorrect: Passed Argument {key}={actual_value} ' \
                f'does not have type {expected_type}.'

    result = func(*args, **kwargs) if not __is_static_method(func=func) else func(**kwargs)
    expected_result_type = annotations['return']

    if isinstance(expected_result_type, str):
        assert result.__class__.__name__ == expected_result_type, \
            f'{__qual_name(func=func)} Type hint is incorrect: Expected: {expected_result_type} ' \
            f'but was {result.__class__.__name__} instead.'
    else:
        assert __is_value_matching_type_hint(value=result, type_hint=expected_result_type, func=func), \
            f'{__qual_name(func=func)} Return type is incorrect: Expected {expected_result_type} ' \
            f'but {result} was the return value which does not match.'
    return result


def __require_docstring_google_format(func: Callable, docstring: Docstring, annotations: Dict[str, Any]) -> None:
    """
        Of course, the params docstring and annotations are obsolete here, but passing saves performance here,
        because they are only calculated once. If we would calculate them here, it would be very expensive.
    """
    num_documented_args = len(docstring.params)
    num_taken_args = len([a for a in annotations if a != 'return'])
    assert num_documented_args == num_taken_args, \
        f'{__qual_name(func=func)} There are {num_documented_args} argument(s) documented, but ' \
        f'{num_taken_args} are actually taken.'

    if docstring.returns is None:
        assert 'return' not in annotations or annotations['return'] is None, \
            f'{__qual_name(func=func)} The return type {annotations["return"]} is not documented.'
    else:
        assert 'return' in annotations and annotations['return'] is not None, \
            f'{__qual_name(func=func)} The return type {docstring.returns.type_name} is documented but the function ' \
            f'does not return anything.'

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
            assert len(docstring.returns.args) == 2, \
                f'{__qual_name(func=func)} Parsing Error. Only Google style Python docstrings are supported.'

            actual_return_type: str = docstring.returns.args[1]
            assert actual_return_type == expected_type, \
                f'{__qual_name(func=func)} Documented type is incorrect: Annotation: {expected_type} ' \
                f'Documented: {actual_return_type}'
        elif annotation != 'return':  # parameters passed to function
            docstring_param = None
            for param in docstring.params:
                if param.arg_name == annotation:
                    docstring_param = param
            assert docstring_param is not None, f'{__qual_name(func=func)} Parameter {annotation} is not documented.'
            assert expected_type == docstring_param.type_name, \
                f'{__qual_name(func=func)} Documented type of parameter {annotation} is incorrect. ' \
                f'Expected {expected_type} but documented is {docstring_param.type_name}.'


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
        assert __is_instance_method(func) or __uses_multiple_decorators(func), \
            f'Function "{func.__name__}" is not an instance method!'
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


def require_kwargs(func: Callable, is_class_decorator: bool = False) -> Callable:
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
        __require_kwargs(func=func, args=args, max_allowed=0 if is_class_decorator else 1)
        return func(*args, **kwargs)
    return wrapper


def validate_args(validator: Callable[[Any], Union[bool, Tuple[bool, str]]],
                  is_class_decorator: bool = False) -> Callable:
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
        def validate(obj: Any) -> None:
            res = validator(obj)
            res, msg = res if type(res) is not bool else (res, 'Invalid arguments.')
            assert res, f'{__qual_name(func=func)} {msg}'

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            args_without_self = __get_args_without_self(func=func,
                                                        args=args,
                                                        max_allowed=0 if is_class_decorator else 1)

            for arg in args_without_self:
                validate(arg)

            for kwarg in kwargs:
                validate(kwargs[kwarg])

            return func(*args, **kwargs)
        return wrapper
    return outer


def require_not_none(func: Callable, is_class_decorator: bool = False) -> Callable:
    """
      Checks that each passed argument is not None and raises AssertionError if there is some.
      Example:
      >>> @require_not_none
      >>> def some_calculation(a, b, c):
      >>>     return a + b + c
   """
    def validator(arg: Any) -> Tuple[bool, str]:
        return arg is not None, f'Argument of function "{func.__name__}" should not be None!'
    return validate_args(validator=validator, is_class_decorator=is_class_decorator)(func)


def require_not_empty_strings(func: Callable, is_class_decorator: bool = False) -> Callable:
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
    return validate_args(validator=validator, is_class_decorator=is_class_decorator)(func)


def pedantic(func: Callable, is_class_decorator: bool = False) -> Callable:
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

    if len(__get_parsed_docstring(func=func).params) > 0:
        __require_docstring_google_format(func=func, annotations=annotations, docstring=docstring)

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        return __require_kwargs_and_type_checking(func=func,
                                                  args=args,
                                                  kwargs=kwargs,
                                                  annotations=annotations,
                                                  signature=inspect.signature(func),
                                                  max_allowed=0 if is_class_decorator else 1
                                                  )
    return wrapper


def pedantic_require_docstring(func: Callable, is_class_decorator: bool = False) -> Callable:
    """It's like pedantic, but now it forces you to write docstrings (Google format)."""

    annotations = __get_annotations(func=func)
    docstring = __get_parsed_docstring(func=func)

    def wrapper(*args, **kwargs) -> Any:
        __require_docstring_google_format(func=func, annotations=annotations, docstring=docstring)
        res = __require_kwargs_and_type_checking(func=func,
                                                 args=args,
                                                 kwargs=kwargs,
                                                 annotations=annotations,
                                                 signature=inspect.signature(func),
                                                 max_allowed=0 if is_class_decorator else 1)
        return res
    return wrapper
