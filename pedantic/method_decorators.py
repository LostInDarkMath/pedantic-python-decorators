import functools
import inspect
from typing import Callable, Any, Tuple, Dict, Type, Union
from datetime import datetime
import warnings
import re

# local file imports
from pedantic.basic_helpers import get_qualified_name_for_err_msg
from pedantic.custom_exceptions import NotImplementedException, TooDirtyException
from pedantic.models.decorated_function import DecoratedFunction
from pedantic.type_hint_parser import _is_instance


def overrides(interface_class: Any) -> Callable[..., Any]:
    """
        Example:
        >>> class Parent:
        ...     def instance_method(self):
        ...         pass
        >>> class Child(Parent):
        ...     @overrides(Parent)
        ...     def instance_method(self):
        ...         print('hi')
    """
    def overrider(func: Callable[..., Any]) -> Callable[..., Any]:
        assert _is_instance_method(func) or _uses_multiple_decorators(func), \
            f'Function "{func.__name__}" is not an instance method!'
        assert (func.__name__ in dir(interface_class)), \
            f"Parent class {interface_class.__name__} does not have such a method '{func.__name__}'."
        return func
    return overrider


def timer(func: Callable[..., Any]) -> Callable[..., Any]:
    """
        Prints how long the execution of the decorated function takes.
        Example:
        >>> @timer
        ... def some_calculation():
        ...     return 42
        >>> some_calculation()
        Timer: Finished function 'some_calculation' in 0:00:00.
        42
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


def count_calls(func: Callable[..., Any]) -> Callable[..., Any]:
    """
        Prints how often the method is called during program execution.
        Example:
        >>> @count_calls
        ... def some_calculation():
        ...    return 42
        >>> some_calculation()
        Count Calls: Call 1 of function 'some_calculation' at ...
        >>> some_calculation()
        Count Calls: Call 2 of function 'some_calculation' at ...
        >>> some_calculation()
        Count Calls: Call 3 of function 'some_calculation' at ...
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        wrapper.num_calls += 1
        print(f"Count Calls: Call {wrapper.num_calls} of function {func.__name__!r} at {datetime.now()}.")
        return func(*args, **kwargs)
    wrapper.num_calls = 0
    return wrapper


def trace(func: Callable[..., Any]) -> Callable[..., Any]:
    """
       Prints the passed posional arguments, keyword arguments and the returned value on each function call.
       Example:
       >>> @trace
       ... def some_calculation(a, b, c):
       ...     return a + b + c
       >>> some_calculation(4, 5, 6)
       Trace: ... calling some_calculation()  with (4, 5, 6), {}
       Trace: ... some_calculation() returned 15
       15
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        print(f'Trace: {datetime.now()} calling {func.__name__}()  with {args}, {kwargs}')
        original_result = func(*args, **kwargs)
        print(f'Trace: {datetime.now()} {func.__name__}() returned {original_result!r}')
        return original_result
    return wrapper


def trace_if_returns(return_value: Any) -> Callable[..., Any]:
    """
       Prints the passed positional and keyword arguments if and only if the decorated function returned return_value.
       This is useful if you want to figure out which input arguments leads to a special return value.
       Example:
       >>> @trace_if_returns(42)
       ... def some_calculation(a, b, c):
       ...     return a + b + c
       >>> some_calculation(1, 2, 3)
       6
       >>> some_calculation(10, 8, 24)
       Function some_calculation returned value 42 for args: (10, 8, 24) and kwargs: {}
       42
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)
            if result == return_value:
                print(f'Function {func.__name__} returned value {result} for args: {args} and kwargs: {kwargs}')
            return result
        return wrapper
    return decorator


def does_same_as_function(other_func: Callable[..., Any]) -> Callable[..., Any]:
    """
        Each time the decorated function is executed, the function other_func is also executed and both results
        will compared. An AssertionError is raised if the results are not equal.
        Example:
        >>> def other_calculation(a, b, c):
        ...     return c + b + a
        >>> @does_same_as_function(other_calculation)
        ... def some_calculation(a, b, c):
        ...     return a + b + c
        >>> some_calculation(1, 2, 3)
        6
    """
    def decorator(decorated_func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(decorated_func)
        def wrapper(*args, **kwargs) -> Any:
            result = decorated_func(*args, **kwargs)
            other = other_func(*args, **kwargs)
            assert other == result, \
                f'Different outputs: Function {decorated_func.__name__} returns {result} and function ' \
                f'{other_func.__name__} returns {other} for parameters {args} {kwargs}'
            return result
        return wrapper
    return decorator


def deprecated(func: Callable[..., Any]) -> Callable[..., Any]:
    """
        This is a decorator which can be used to mark functions as deprecated. It will result in a warning being emitted
        when the function is used.
        Example:
        >>> @deprecated
        ... def some_calculation(a, b, c):
        ...     pass
        >>> some_calculation(5, 4, 3)
    """
    @functools.wraps(func)
    def new_func(*args, **kwargs) -> Any:
        _raise_warning(msg="Call to deprecated function {}.".format(func.__name__), category=DeprecationWarning)
        return func(*args, **kwargs)
    return new_func


def needs_refactoring(func: Callable[..., Any]) -> Callable[..., Any]:
    """
        Of course, you refactor immediately if you see something ugly.
        However, if you don't have the time for a big refactoring use this decorator at least.
        A warning is printed everytime the decorated function is called.
        Example:
        >>> @needs_refactoring
        ... def some_calculation(a, b, c):
        ...     pass
        >>> some_calculation(5, 4, 3)
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        _raise_warning(msg=f'Function "{func.__name__}" looks terrible and needs a refactoring!', category=UserWarning)
        return func(*args, **kwargs)
    return wrapper


def unimplemented(func: Callable[..., Any]) -> Callable[..., Any]:
    """
        For documentation purposes. Throw NotImplementedException if the function is called.
        Example:
        >>> @unimplemented
        ... def some_calculation(a, b, c):
        ...     pass
        >>> some_calculation(5, 4, 3)
        Traceback (most recent call last):
        ...
        pedantic.custom_exceptions.NotImplementedException: Function "some_calculation" is not implemented yet!
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        raise NotImplementedException(f'Function "{func.__name__}" is not implemented yet!')
    return wrapper


def dirty(func: Callable[..., Any]) -> Callable[..., Any]:
    """
        Prevents dirty code from beeing executed.
        Example:
        >>> @dirty
        ... def some_calculation(a, b, c):
        ...     return a + a + a + a + a
        >>> some_calculation(5, 4, 3)
        Traceback (most recent call last):
        ...
        pedantic.custom_exceptions.TooDirtyException: Function "some_calculation" is too dirty to be executed!
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        raise TooDirtyException(f'Function "{func.__name__}" is too dirty to be executed!')
    return wrapper


def require_kwargs(func: Callable[..., Any], is_class_decorator: bool = False) -> Callable[..., Any]:
    """
        Checks that each passed argument is a keyword argument.
        Example:
        >>> @require_kwargs
        ... def some_calculation(a, b, c):
        ...     return a + b + c
        >>> some_calculation(5, 4, 3)
        Traceback (most recent call last):
        ...
        AssertionError: In function some_calculation:
         Use kwargs when you call function some_calculation. Args: (5, 4, 3)
        >>> some_calculation(a=5, b=4, c=3)
        12
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        _assert_uses_kwargs(func=func, args=args, is_class_decorator=is_class_decorator)
        return func(*args, **kwargs)
    return wrapper


def validate_args(validator: Callable[[Any], Union[bool, Tuple[bool, str]]],
                  is_class_decorator: bool = False) -> Callable[..., Any]:
    """
      Validates each passed argument with the given validator.
      Example:
      >>> @validate_args(lambda x: (x > 42, f'Each argument should be greater then 42, but it was {x}.'))
      ... def some_calculation(a, b, c):
      ...     return a + b + c
      >>> some_calculation(80, 40, 50)
      Traceback (most recent call last):
      ...
      AssertionError: In function some_calculation:
       Each argument should be greater then 42, but it was 40.
      >>> some_calculation(43, 48, 50)
      141
   """
    def outer(func: Callable[..., Any]) -> Callable[..., Any]:
        def validate(obj: Any) -> None:
            res = validator(obj)
            res, msg = res if type(res) is not bool else (res, 'Invalid arguments.')
            assert res, f'{get_qualified_name_for_err_msg(func=func)} {msg}'

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            args_without_self = _get_args_without_self(f=func, args=args, is_class_decorator=is_class_decorator)

            for arg in args_without_self:
                validate(arg)

            for kwarg in kwargs:
                validate(kwargs[kwarg])

            return func(*args, **kwargs)
        return wrapper
    return outer


def require_not_none(func: Callable[..., Any], is_class_decorator: bool = False) -> Callable[..., Any]:
    """
      Checks that each passed argument is not None and raises AssertionError if there is some.
      Example:
      >>> @require_not_none
      ... def some_calculation(a, b, c):
      ...     return a + b + c
      >>> some_calculation(80, None, 50)
      Traceback (most recent call last):
      ...
      AssertionError: In function some_calculation:
       Argument of function "some_calculation" should not be None!
      >>> some_calculation(43, 48, 50)
      141
   """
    def validator(arg: Any) -> Tuple[bool, str]:
        return arg is not None, f'Argument of function "{func.__name__}" should not be None!'
    return validate_args(validator=validator, is_class_decorator=is_class_decorator)(func)


def require_not_empty_strings(func: Callable[..., Any], is_class_decorator: bool = False) -> Callable[..., Any]:
    """
       Throw a ValueError if the arguments are None, not strings, or empty strings or contains only whitespaces.
       Example:
       >>> @require_not_empty_strings
       ... def some_calculation(a, b, c):
       ...     print(a, b, c)
       >>> some_calculation('Hi', '   ', 'you')
       Traceback (most recent call last):
       ...
       AssertionError: In function some_calculation:
        Arguments of function "some_calculation" should be a not empty string! Got:
       >>> some_calculation('Hi', None, 'you')
       Traceback (most recent call last):
       ...
       AssertionError: In function some_calculation:
        Arguments of function "some_calculation" should be a not empty string! Got:None
       >>> some_calculation('Hi', 42, 'you')
       Traceback (most recent call last):
       ...
       AssertionError: In function some_calculation:
        Arguments of function "some_calculation" should be a not empty string! Got:42
   """
    def validator(arg: Any) -> Tuple[bool, str]:
        return arg is not None and type(arg) is str and len(arg.strip()) > 0, \
            f'Arguments of function "{func.__name__}" should be a not empty string! Got:{str(arg).strip()}'
    return validate_args(validator=validator, is_class_decorator=is_class_decorator)(func)


def pedantic(func: Callable[..., Any], is_class_decorator: bool = False) -> Callable[..., Any]:
    """
       Checks the types and throw an AssertionError if a type is incorrect.
       This decorator reads the type hints and use them as contracts that will be checked.
       If the function misses type hints, it will raise an AssertionError.
       It also forces the usage of keyword arguments.

       Example:
       >>> @pedantic
       ... def some_calculation(a: int, b: float, c: str) -> bool:
       ...     return float(a) == b and str(b) == c
       >>> some_calculation(a=42.0, b=14.0, c='you')
       Traceback (most recent call last):
       ...
       AssertionError: In function some_calculation:
        Type hint is incorrect: Passed Argument a=42.0 does not have type <class 'int'>.
       >>> some_calculation(a=42, b=None, c='you')
       Traceback (most recent call last):
       ...
       AssertionError: In function some_calculation:
        Type hint is incorrect: Passed Argument b=None does not have type <class 'float'>.
       >>> some_calculation(a=42, b=42, c='you')
       Traceback (most recent call last):
       ...
       AssertionError: In function some_calculation:
        Type hint is incorrect: Passed Argument b=42 does not have type <class 'float'>.
       >>> some_calculation(5, 4.0, 'hi')
       Traceback (most recent call last):
       ...
       AssertionError: In function some_calculation:
        Use kwargs when you call function some_calculation. Args: (5, 4.0, 'hi')
   """

    decorated_func = DecoratedFunction(func=func)

    if len(decorated_func.docstring.params) > 0:
        _assert_has_correct_docstring(decorated_func=decorated_func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        return _assert_has_kwargs_and_correct_type_hints(decorated_func=decorated_func,
                                                         args=args,
                                                         kwargs=kwargs,
                                                         is_class_decorator=is_class_decorator)
    return wrapper


def pedantic_require_docstring(func: Callable[..., Any], is_class_decorator: bool = False) -> Callable[..., Any]:
    """Same as pedantic, but now it forces you to write docstrings (Google style)."""
    decorated_func = DecoratedFunction(func=func)
    _assert_has_correct_docstring(decorated_func=decorated_func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        res = _assert_has_kwargs_and_correct_type_hints(decorated_func=decorated_func,
                                                        args=args,
                                                        kwargs=kwargs,
                                                        is_class_decorator=is_class_decorator)
        return res
    return wrapper


def _assert_has_kwargs_and_correct_type_hints(decorated_func: DecoratedFunction,
                                              args: Tuple[Any, ...],
                                              kwargs: Dict[str, Any],
                                              is_class_decorator: bool) -> Any:
    func = decorated_func.func
    params = decorated_func.signature.parameters
    err = decorated_func.err
    type_vars = {}

    _assert_uses_kwargs(func=func, args=args, is_class_decorator=is_class_decorator)

    assert decorated_func.signature.return_annotation is not inspect.Signature.empty, \
        f'{err} Their should be a type hint for the return type (e.g. None if there is nothing returned).'

    i = 1 if _is_instance_method(func=func) else 0
    for key in params:
        param = params[key]
        expected_type = param.annotation

        if param.name == 'self':
            continue

        assert expected_type is not inspect.Signature.empty, f'{err} Parameter "{param.name}" should have a type hint.'

        if param.default is inspect.Signature.empty:
            if _is_func_that_require_kwargs(func=func):
                assert key in kwargs, f'{err} Parameter "{key}" is unfilled.'
                actual_value = kwargs[key]
            else:
                actual_value = args[i]
                i += 1
        else:
            actual_value = kwargs[key] if key in kwargs else param.default

        if isinstance(expected_type, str):
            class_name = actual_value.__class__.__name__
            assert class_name == expected_type, \
                f'{err} Type hint is incorrect. Expected: {expected_type} but was {class_name} instead.'
        else:
            assert _is_value_matching_type_hint(value=actual_value, type_hint=expected_type,
                                                err_prefix=err, type_vars=type_vars), \
                f'{err} Type hint is incorrect: ' \
                f'Passed Argument {key}={actual_value} does not have type {expected_type}.'

    result = func(*args, **kwargs) if not _is_static_method(func=func) else func(**kwargs)
    expected_result_type = decorated_func.annotations['return']

    if isinstance(expected_result_type, str):
        assert result.__class__.__name__ == expected_result_type, \
            f'{err} Type hint is incorrect: Expected: {expected_result_type} ' \
            f'but was {result.__class__.__name__} instead.'
    else:
        assert _is_value_matching_type_hint(value=result, type_hint=expected_result_type,
                                            err_prefix=err, type_vars=type_vars), \
            f'{err} Return type is incorrect: Expected {expected_result_type} ' \
            f'but {result} was the return value which does not match.'
    return result


def _assert_has_correct_docstring(decorated_func: DecoratedFunction) -> None:
    annotations = decorated_func.annotations
    docstring = decorated_func.docstring
    err_prefix = decorated_func.err

    raw_doc = decorated_func.func.__doc__
    assert raw_doc is not None and raw_doc != '', f'{err_prefix} The function should have a docstring!'

    num_documented_args = len(docstring.params)
    num_taken_args = len([a for a in annotations if a != 'return'])
    assert num_documented_args == num_taken_args, \
        f'{err_prefix} There are {num_documented_args} argument(s) documented, but {num_taken_args} are actually taken.'

    if docstring.returns is None:
        assert 'return' not in annotations or annotations['return'] is None, \
            f'{err_prefix} The return type {annotations["return"]} is not documented.'
    else:
        assert 'return' in annotations and annotations['return'] is not None, \
            f'{err_prefix} The return type {docstring.returns.type_name} ' \
            f'is documented but the function does not return anything.'

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
                f'{err_prefix} Parsing Error. Only Google style Python docstrings are supported.'

            actual_return_type: str = docstring.returns.args[1]
            assert actual_return_type == expected_type, \
                f'{err_prefix} Documented type is incorrect: Annotation: {expected_type} ' \
                f'Documented: {actual_return_type}'
        elif annotation != 'return':  # parameters passed to function
            docstring_param = None
            for param in docstring.params:
                if param.arg_name == annotation:
                    docstring_param = param
            assert docstring_param is not None, \
                f'{err_prefix} Parameter {annotation} is not documented.'
            assert expected_type == docstring_param.type_name, \
                f'{err_prefix} Documented type of parameter {annotation} is incorrect. ' \
                f'Expected {expected_type} but documented is {docstring_param.type_name}.'


def _assert_uses_kwargs(func: Callable[..., Any], args: Tuple[Any, ...], is_class_decorator: bool) -> None:
    if _is_func_that_require_kwargs(func=func):
        args_without_self = _get_args_without_self(f=func, args=args, is_class_decorator=is_class_decorator)
        assert args_without_self == (), \
            f'{get_qualified_name_for_err_msg(func=func)} Use kwargs when you call function {func.__name__}. ' \
            f'Args: {args_without_self}'


def _get_args_without_self(f: Callable[..., Any], args: Tuple[Any, ...], is_class_decorator: bool) -> Tuple[Any, ...]:
    max_allowed = 0 if is_class_decorator else 1
    if _is_instance_method(f) or _is_static_method(f) or _uses_multiple_decorators(f, max_allowed):
        return args[1:]  # self is always the first argument if present
    return args


def _is_func_that_require_kwargs(func: Callable[..., Any]) -> bool:
    f_name = func.__name__

    if _is_property_setter(func=func):
        return False

    if not f_name.startswith('__') or not f_name.endswith('__'):
        return True

    return f_name in ['__new__', '__init__', '__str__', '__del__', '__int__', '__float__', '__complex__', '__oct__',
                      '__hex__', '__index__', '__trunc__', '__repr__', '__unicode__', '__hash__', '__nonzero__',
                      '__dir__', '__sizeof__']


def _is_property_setter(func: Callable[..., Any]) -> bool:
    return f'@{func.__name__}.setter' in inspect.getsource(func)


def _is_instance_method(func: Callable[..., Any]) -> bool:
    spec = inspect.getfullargspec(func)
    return spec.args and spec.args[0] == 'self'


def _is_static_method(func: Callable[..., Any]) -> bool:
    return '@staticmethod' in inspect.getsource(func)


def _uses_multiple_decorators(func: Callable[..., Any], max_allowed: int = 1) -> bool:
    return len(re.findall('@', inspect.getsource(func).split('def')[0])) > max_allowed


def _is_value_matching_type_hint(value: Any, type_hint: Any, err_prefix: str, type_vars: Dict[type, Any]) -> bool:
    """
    Wrapper for file "type_hint_parser.py".
    NOTE: Type hint "Dict[TypeVar, Any]" crashes in Python 3.6. So "Dict[type, Any]" must be used here.
    """

    if type_hint is None:
        return value == type_hint
    assert type(type_hint) is not tuple, f'{err_prefix} Use "Tuple[]" instead of "{type_hint}" as type hint.'
    assert type_hint is not tuple, f'{err_prefix} Use "Tuple[]" instead of "tuple" as type hint.'
    assert type_hint is not list, f'{err_prefix} Use "List[]" instead of "list" as type hint.'
    assert type_hint is not dict, f'{err_prefix} Use "Dict[]" instead of "dict" as type hint.'
    assert type_hint is not set, f'{err_prefix} Use "Set[]" instead of "set" as type hint.'
    assert type_hint is not frozenset, f'{err_prefix} Use "FrozenSet[]" instead of "frozenset" as type hint.'

    try:
        return _is_instance(value, type_hint, type_vars)
    except AssertionError as ex:
        raise AssertionError(f'{err_prefix} {ex}')
    except (AttributeError, Exception) as ex:
        raise AssertionError(f'{err_prefix} An error occurred during type hint checking. Value: {value} Annotation: '
                             f'{type_hint} Mostly this is caused by an incorrect type annotation. Details: {ex} ')


def _raise_warning(msg: str, category: Type[Warning]):
    warnings.simplefilter('always', category)  # turn off filter
    warnings.warn(msg, category=category, stacklevel=2)
    warnings.simplefilter('default', category)  # reset filter


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
