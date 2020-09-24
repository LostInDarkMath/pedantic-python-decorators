import functools
import inspect
import sys
from typing import Callable, Any, Tuple, Dict, Type, Union, Optional, List
from datetime import datetime
import warnings

from pedantic.basic_helpers import get_qualified_name_for_err_msg, TYPE_VAR_METHOD_NAME
from pedantic.custom_exceptions import NotImplementedException, TooDirtyException
from pedantic.models.decorated_function import DecoratedFunction
from pedantic.type_hint_parser import _is_instance, _get_type_arguments


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
        deco_func = DecoratedFunction(func=func)
        uses_multiple_decorators = deco_func.num_of_decorators > 1
        assert deco_func.is_instance_method or uses_multiple_decorators, \
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
        Timer: Finished function "some_calculation" in 0:00:00...
        42
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time: datetime = datetime.now()
        value: Any = func(*args, **kwargs)
        end_time = datetime.now()
        run_time = end_time - start_time
        print(f'Timer: Finished function "{func.__name__}" in {run_time}.')
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
    def wrapper(*args: Any, **kwargs: Any) -> Any:
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
    def wrapper(*args: Any, **kwargs: Any) -> Any:
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
        def wrapper(*args: Any, **kwargs: Any) -> Any:
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
        def wrapper(*args: Any, **kwargs: Any) -> Any:
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
        Use this decorator to mark a function as deprecated. It will raise a warning when the function is called.
        Example:
        >>> @deprecated
        ... def some_calculation(a, b, c):
        ...     pass
        >>> some_calculation(5, 4, 3)
    """

    @functools.wraps(func)
    def new_func(*args: Any, **kwargs: Any) -> Any:
        _raise_warning(msg=f'Call to deprecated function "{func.__name__}".', category=DeprecationWarning)
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
    def wrapper(*args: Any, **kwargs: Any) -> Any:
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
    def wrapper(*args: Any, **kwargs: Any) -> Any:
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
    def wrapper(*args: Any, **kwargs: Any) -> Any:
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
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        _assert_uses_kwargs(func=DecoratedFunction(func=func), args=args, is_class_decorator=is_class_decorator)
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
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            args_without_self = _get_args_without_self(func=DecoratedFunction(func=func),
                                                       args=args, is_class_decorator=is_class_decorator)

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


def pedantic(func: Optional[Callable[..., Any]] = None,
             is_class_decorator: bool = False,
             require_docstring: bool = False,
             ) -> Callable[..., Any]:
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

    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        decorated_func = DecoratedFunction(func=f)

        if require_docstring or len(decorated_func.docstring.params) > 0:
            _assert_has_correct_docstring(decorated_func=decorated_func)

        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if decorated_func.is_instance_method and hasattr(args[0], TYPE_VAR_METHOD_NAME):
                type_vars = getattr(args[0], TYPE_VAR_METHOD_NAME)()
            else:
                type_vars = dict()

            _assert_uses_kwargs(func=decorated_func, args=args, is_class_decorator=is_class_decorator)
            return _check_types(decorated_func=decorated_func, args=args, kwargs=kwargs, type_vars=type_vars)
        return wrapper
    return decorator if func is None else decorator(f=func)


def pedantic_require_docstring(func: Optional[Callable[..., Any]] = None, **kwargs: Any) -> Callable[..., Any]:
    """Shortcut for @pedantic(require_docstring=True) """
    return pedantic(func=func, require_docstring=True, **kwargs)


def _check_types(decorated_func: DecoratedFunction, args: Tuple[Any, ...],
                 kwargs: Dict[str, Any],
                 type_vars: Dict[Any, Any]) -> Any:
    func = decorated_func.func
    params = decorated_func.signature.parameters
    err = decorated_func.err
    already_checked_kwargs = []

    assert decorated_func.signature.return_annotation is not inspect.Signature.empty, \
        f'{err} There should be a type hint for the return type (e.g. None if there is nothing returned).'

    arg_index = 1 if decorated_func.is_instance_method else 0

    for key in params:
        param = params[key]
        expected_type = param.annotation

        if param.name == 'self':
            continue

        assert expected_type is not inspect.Signature.empty, f'{err} Parameter "{param.name}" should have a type hint.'

        if str(param).startswith('*') and not str(param).startswith('**'):
            for arg in args:
                assert _is_value_matching_type_hint(value=arg, type_hint=expected_type,
                                                    err_prefix=err, type_vars=type_vars), \
                    f'{err} Type hint is incorrect: Passed argument {arg} does not have type {expected_type}.'
            continue

        if str(param).startswith('**'):
            for kwarg in kwargs:
                if kwarg in already_checked_kwargs:
                    continue

                actual_value = kwargs[kwarg]
                assert _is_value_matching_type_hint(value=actual_value, type_hint=expected_type,
                                                    err_prefix=err, type_vars=type_vars), \
                    f'{err} Type hint is incorrect: ' \
                    f'Passed Argument {kwarg}={actual_value} does not have type {expected_type}.'
            continue

        if param.default is inspect.Signature.empty:
            if decorated_func.should_have_kwargs:
                assert key in kwargs, f'{err} Parameter "{key}" is unfilled.'
                actual_value = kwargs[key]
            else:
                actual_value = args[arg_index]
                arg_index += 1
        else:
            actual_value = kwargs[key] if key in kwargs else param.default

        assert _is_value_matching_type_hint(value=actual_value, type_hint=expected_type,
                                            err_prefix=err, type_vars=type_vars), \
            f'{err} Type hint is incorrect: ' \
            f'Passed Argument {key}={actual_value} does not have type {expected_type}.'

        already_checked_kwargs.append(key)

    result = func(*args, **kwargs) if not decorated_func.is_static_method else func(**kwargs)
    expected_result_type = decorated_func.annotations['return']

    assert _is_value_matching_type_hint(value=result, type_hint=expected_result_type,
                                        err_prefix=err, type_vars=type_vars), \
        f'{err} Return type is incorrect: Expected {expected_result_type} ' \
        f'but {result} was the return value which does not match.'
    return result


def _assert_has_correct_docstring(decorated_func: DecoratedFunction) -> None:
    annotations = decorated_func.annotations
    docstring = decorated_func.docstring
    err_prefix = decorated_func.err
    context = {}

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
        expected_type = annotations[annotation]
        _update_context(context=context, type_=expected_type)

        if annotation == 'return' and annotations[annotation] is not None:
            assert len(docstring.returns.args) == 2, \
                f'{err_prefix} Parsing Error. Only Google style Python docstrings are supported.'

            actual_return_type = _parse_documented_type(
                type_=docstring.returns.args[1], context=context, err=err_prefix)
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
            actual_param_type = _parse_documented_type(
                type_=docstring_param.type_name, context=context, err=err_prefix)
            assert expected_type == actual_param_type, \
                f'{err_prefix} Documented type of parameter {annotation} is incorrect. ' \
                f'Expected {expected_type} but documented is {actual_param_type}.'


def _parse_documented_type(type_: str, context: Dict[str, Any], err: str) -> Any:
    """
    >>> import sys
    >>> _parse_documented_type(type_='List[str]', context={}, err='')
    typing.List[str]
    >>> _parse_documented_type(type_='float', context={}, err='')
    <class 'float'>
    >>> _parse_documented_type(type_='List[List[bool]]', context={}, err='')
    typing.List[typing.List[bool]]
    >>> _parse_documented_type(type_='Union[int, float, str]', context={}, err='')
    typing.Union[int, float, str]
    >>> _parse_documented_type(type_='Callable[[int, bool, str], float]', context={}, err='')
    typing.Callable[[int, bool, str], float]
    >>> _parse_documented_type(type_='Optional[List[Dict[str, float]]]', context={}, err='') \
        if sys.version_info < (3, 9) else print('typing.Union[typing.List[typing.Dict[str, float]], NoneType]')
    typing.Union[typing.List[typing.Dict[str, float]], NoneType]
    >>> _parse_documented_type(type_='Optional[List[Dict[str, float]]]', context={}, err='') \
        if sys.version_info >= (3, 9) else print('typing.Optional[typing.List[typing.Dict[str, float]]]')
    typing.Optional[typing.List[typing.Dict[str, float]]]
    >>> _parse_documented_type(type_='Union[List[Dict[str, float]], None]', context={}, err='') \
        if sys.version_info < (3, 9) else print('typing.Union[typing.List[typing.Dict[str, float]], NoneType]')
    typing.Union[typing.List[typing.Dict[str, float]], NoneType]
    >>> _parse_documented_type(type_='Union[List[Dict[str, float]], None]', context={}, err='') \
        if sys.version_info >= (3, 9) else print('typing.Optional[typing.List[typing.Dict[str, float]]]')
    typing.Optional[typing.List[typing.Dict[str, float]]]
    >>> _parse_documented_type(type_='MyClass', context={}, err='')
    Traceback (most recent call last):
    ...
    AssertionError:  Documented type "MyClass" was not found.
    >>> class MyClass: pass
    >>> _parse_documented_type(type_='MyClass', context={'MyClass': MyClass}, err='')
    <class 'pedantic.method_decorators.MyClass'>
    >>> _parse_documented_type(type_='MyClas', context={'MyClass': MyClass}, err='')
    Traceback (most recent call last):
    ...
    AssertionError:  Documented type "MyClas" was not found. Maybe you meant "MyClass"
    >>> class MyClub: pass
    >>> _parse_documented_type(type_='MyClas', context={'MyClass': MyClass, 'MyClub': MyClub}, err='')
    Traceback (most recent call last):
    ...
    AssertionError:  Documented type "MyClas" was not found. Maybe you meant one of the following: ['MyClass', 'MyClub']
    """

    assert 'typing.' not in type_, f'{err} Do not use "typing." in docstring. Please replace "{type_}" with ' \
                                   f'"{type_.replace("typing.", "")}" in  the docstring'

    try:
        return eval(type_, globals(), context)
    except NameError:
        possible_meant_types = [t for t in context.keys() if isinstance(t, str)]
        if len(possible_meant_types) > 1:
            msg = f' Maybe you meant one of the following: {possible_meant_types}'
        elif len(possible_meant_types) == 1:
            msg = f' Maybe you meant "{possible_meant_types[0]}"'
        else:
            msg = ''
        raise AssertionError(f'{err} Documented type "{type_}" was not found.{msg}')


def _update_context(context: Dict[str, Any], type_: Any) -> Dict[str, Any]:
    """
        >>> from typing import List, Union, Optional, Callable
        >>> _update_context(type_=None, context={})
        {}
        >>> _update_context(type_=None, context={'a': 1, 'b': 2})
        {'a': 1, 'b': 2}
        >>> _update_context(type_=float, context={})
        {'float': <class 'float'>}
        >>> _update_context(type_=List[str], context={})
        {'str': <class 'str'>}
        >>> _update_context(type_=List[List[bool]], context={})
        {'bool': <class 'bool'>}
        >>> _update_context(type_=Union[int, float, str], context={})
        {'int': <class 'int'>, 'float': <class 'float'>, 'str': <class 'str'>}
        >>> _update_context(type_=Callable[[int, bool, str], float], context={})
        {'int': <class 'int'>, 'bool': <class 'bool'>, 'str': <class 'str'>, 'float': <class 'float'>}
        >>> _update_context(type_=Optional[List[Dict[str, float]]], context={})
        {'str': <class 'str'>, 'float': <class 'float'>, 'NoneType': <class 'NoneType'>}
        >>> _update_context(type_=Union[List[Dict[str, float]], None], context={})
        {'str': <class 'str'>, 'float': <class 'float'>, 'NoneType': <class 'NoneType'>}
        >>> _update_context(type_='MyClass', context={})
        {'MyClass': 'MyClass'}
        >>>
    """

    if isinstance(type_, str):
        context[type_] = type_
    elif str(type_).startswith('typing'):
        type_arguments = _get_type_arguments(cls=type_)

        for type_argument in type_arguments:
            if isinstance(type_argument, list):  # Callable has a List of Types as first argument
                for type_arg in type_argument:
                    _update_context(context=context, type_=type_arg)
            _update_context(context=context, type_=type_argument)
    elif hasattr(type_, '__name__'):
        context[type_.__name__] = type_
    return context


def _assert_uses_kwargs(func: DecoratedFunction, args: Tuple[Any, ...], is_class_decorator: bool) -> None:
    """
       >>> def f1(): pass
       >>> f1 = DecoratedFunction(f1)
       >>> _assert_uses_kwargs(f1, (), False)
       >>> def f2(a, b, c): pass
       >>> f2 = DecoratedFunction(f2)
       >>> _assert_uses_kwargs(f2, (3, 4, 5), False)
       Traceback (most recent call last):
       ...
       AssertionError: In function f2:
        Use kwargs when you call function f2. Args: (3, 4, 5)
       >>> _assert_uses_kwargs(f2, (), False)
       >>> class A:
       ...    def f(self): pass
       ...    @staticmethod
       ...    def g(arg=42): pass
       ...    def __compare__(self, other): pass
       >>> a = A()
       >>> _assert_uses_kwargs(DecoratedFunction(A.f), (a,), False)
       >>> _assert_uses_kwargs(DecoratedFunction(A.g), (a,), False)
       >>> _assert_uses_kwargs(DecoratedFunction(A.g), (a, 45), False)
       Traceback (most recent call last):
       ...
       AssertionError: In function A.g:
        Use kwargs when you call function g. Args: (45,)
       >>> _assert_uses_kwargs(DecoratedFunction(A.__compare__), (a, 'hi',), False)
       >>> _assert_uses_kwargs(DecoratedFunction(A.__compare__), (a,), False)
    """
    if func.should_have_kwargs:
        args_without_self = _get_args_without_self(func=func, args=args, is_class_decorator=is_class_decorator)
        assert args_without_self == (), \
            f'{func.err} Use kwargs when you call function {func.name}. ' \
            f'Args: {args_without_self}'


def _get_args_without_self(func: DecoratedFunction, args: Tuple[Any, ...], is_class_decorator: bool) -> Tuple[Any, ...]:
    """
       >>> def f1(): pass
       >>> _get_args_without_self(DecoratedFunction(f1), (), False)
       ()
       >>> def f2(a, b, c): pass
       >>> _get_args_without_self(DecoratedFunction(f2), (3, 4, 5), False)
       (3, 4, 5)
       >>> class A:
       ...    def f(self): pass
       ...    @staticmethod
       ...    def g(): pass
       ...    def __compare__(self, other): pass
       >>> a = A()
       >>> _get_args_without_self(DecoratedFunction(A.f), (a,), False)
       ()
       >>> _get_args_without_self(DecoratedFunction(A.g), (a,), False)
       ()
       >>> _get_args_without_self(DecoratedFunction(A.__compare__), (a, 'hi',), False)
       ('hi',)
    """
    max_allowed = 0 if is_class_decorator else 1
    uses_multiple_decorators = func.num_of_decorators > max_allowed
    if func.is_instance_method or func.is_static_method or uses_multiple_decorators:
        return args[1:]  # self is always the first argument if present
    return args


def _is_value_matching_type_hint(value: Any, type_hint: Any, err_prefix: str, type_vars: Dict[type, Any]) -> bool:
    """
        Wrapper for file "type_hint_parser.py".
        The type hint "Dict[TypeVar, Any]" for type_vars crashes in Python 3.6. So "Dict[type, Any]" must be used here.

        >>> from typing import List, Union, Optional, Callable, Any
        >>> _is_value_matching_type_hint(5, int, '', {})
        True
        >>> _is_value_matching_type_hint(5, float, '', {})
        False
        >>> _is_value_matching_type_hint('hi', str, '', {})
        True
        >>> _is_value_matching_type_hint(None, str, '', {})
        False
        >>> _is_value_matching_type_hint(None, Any, '', {})
        True
        >>> _is_value_matching_type_hint(None, None, '', {})
        True
        >>> _is_value_matching_type_hint(5, Any, '', {})
        True
        >>> _is_value_matching_type_hint(3.1415, float, '', {})
        True
        >>> _is_value_matching_type_hint([1, 2, 3, 4], List[int], '', {})
        True
        >>> _is_value_matching_type_hint([1, 2, 3.0, 4], List[int], '', {})
        False
        >>> _is_value_matching_type_hint([1, 2, 3.0, 4], List[float], '', {})
        False
        >>> _is_value_matching_type_hint([1, 2, 3.0, 4], List[Union[float, int]], '', {})
        True
        >>> _is_value_matching_type_hint([[True, False], [False], [True], []], List[List[bool]], '', {})
        True
        >>> _is_value_matching_type_hint([[True, False, 1], [False], [True], []], List[List[bool]], '', {})
        False
        >>> _is_value_matching_type_hint(5, Union[int, float, bool], '', {})
        True
        >>> _is_value_matching_type_hint(5.0, Union[int, float, bool], '', {})
        True
        >>> _is_value_matching_type_hint(False, Union[int, float, bool], '', {})
        True
        >>> _is_value_matching_type_hint('5', Union[int, float, bool], '', {})
        False
        >>> def f(a: int, b: bool, c: str) -> float: pass
        >>> _is_value_matching_type_hint(f, Callable[[int, bool, str], float], '', {})
        True
        >>> _is_value_matching_type_hint(None, Optional[List[Dict[str, float]]], '', {})
        True
        >>> _is_value_matching_type_hint([{'a': 1.2, 'b': 3.4}], Optional[List[Dict[str, float]]], '', {})
        True
        >>> _is_value_matching_type_hint([{'a': 1.2, 'b': 3}], Optional[List[Dict[str, float]]], '', {})
        False
        >>> _is_value_matching_type_hint({'a': 1.2, 'b': 3.4}, Optional[List[Dict[str, float]]], '', {})
        False
        >>> _is_value_matching_type_hint([{'a': 1.2, 7: 3.4}], Optional[List[Dict[str, float]]], '', {})
        False
        >>> class MyClass: pass
        >>> _is_value_matching_type_hint(MyClass(), 'MyClass', '', {})
        True
        >>> _is_value_matching_type_hint(MyClass(), 'MyClas', '', {})
        False
        >>> _is_value_matching_type_hint([1, 2, 3], list, '', {})
        Traceback (most recent call last):
        ...
        AssertionError:  Use "List[]" instead of "list" as type hint.
        >>> _is_value_matching_type_hint((1, 2, 3), tuple, '', {})
        Traceback (most recent call last):
        ...
        AssertionError:  Use "Tuple[]" instead of "tuple" as type hint.
        >>> _is_value_matching_type_hint({1: 1.0, 2: 2.0, 3: 3.0}, dict, '', {})
        Traceback (most recent call last):
        ...
        AssertionError:  Use "Dict[]" instead of "dict" as type hint.
    """

    if type_hint is None:
        return value == type_hint
    elif isinstance(type_hint, str):
        class_name = value.__class__.__name__
        return class_name == type_hint

    assert type(type_hint) is not tuple, f'{err_prefix} Use "Tuple[]" instead of "{type_hint}" as type hint.'
    assert type_hint is not tuple, f'{err_prefix} Use "Tuple[]" instead of "tuple" as type hint.'
    assert type_hint is not list, f'{err_prefix} Use "List[]" instead of "list" as type hint.'
    assert type_hint is not dict, f'{err_prefix} Use "Dict[]" instead of "dict" as type hint.'
    assert type_hint is not set, f'{err_prefix} Use "Set[]" instead of "set" as type hint.'
    assert type_hint is not frozenset, f'{err_prefix} Use "FrozenSet[]" instead of "frozenset" as type hint.'

    try:
        return _is_instance(obj=value, type_=type_hint, type_vars=type_vars)
    except AssertionError as ex:
        raise AssertionError(f'{err_prefix} {ex}')
    except (AttributeError, Exception) as ex:
        raise AssertionError(f'{err_prefix} An error occurred during type hint checking. Value: {value} Annotation: '
                             f'{type_hint} Mostly this is caused by an incorrect type annotation. Details: {ex} ')


def _raise_warning(msg: str, category: Type[Warning]) -> None:
    warnings.simplefilter(action='always', category=category)
    warnings.warn(message=msg, category=category, stacklevel=2)
    warnings.simplefilter(action='default', category=category)


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
