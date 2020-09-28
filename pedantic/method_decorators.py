import functools
import inspect
import sys
from typing import Callable, Any, Tuple, Dict, Type, Union, Optional, List, Mapping
from datetime import datetime
import warnings

from pedantic.set_envionment_variables import is_enabled
from pedantic.constants import TYPE_VAR_METHOD_NAME, TypeVar, ReturnType, F
from pedantic.exceptions import NotImplementedException, TooDirtyException, PedanticOverrideException, \
    PedanticTypeCheckException, PedanticException, PedanticDocstringException, PedanticCallWithArgsException, \
    PedanticTypeVarMismatchException
from pedantic.models.decorated_function import DecoratedFunction
from pedantic.type_hint_parser import _is_instance, _get_type_arguments


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


def require_kwargs(func: F, is_class_decorator: bool = False) -> F:
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
        _assert_uses_kwargs(func=DecoratedFunction(func=func), args=args, is_class_decorator=is_class_decorator)
        return func(*args, **kwargs)
    return wrapper


def validate_args(validator: Callable[[Any], Union[bool, Tuple[bool, str]]], is_class_decorator: bool = False) -> F:
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
                raise AssertionError(f'{deco_func.err} {msg}')

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            args_without_self = _get_args_without_self(func=deco_func, args=args, is_class_decorator=is_class_decorator)

            for arg in args_without_self:
                validate(arg)

            for kwarg in kwargs:
                validate(kwargs[kwarg])

            return func(*args, **kwargs)
        return wrapper
    return outer


def pedantic(func: Optional[F] = None, is_class_decorator: bool = False, require_docstring: bool = False) -> F:
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
       >>> my_function(a=42.0, b=14.0, c='you')
       Traceback (most recent call last):
       ...
       pedantic.exceptions.PedanticTypeCheckException: In function my_function:
        Type hint is incorrect: Passed Argument a=42.0 does not have type <class 'int'>.
       >>> my_function(a=42, b=None, c='you')
       Traceback (most recent call last):
       ...
       pedantic.exceptions.PedanticTypeCheckException: In function my_function:
        Type hint is incorrect: Passed Argument b=None does not have type <class 'float'>.
       >>> my_function(a=42, b=42, c='you')
       Traceback (most recent call last):
       ...
       pedantic.exceptions.PedanticTypeCheckException: In function my_function:
        Type hint is incorrect: Passed Argument b=42 does not have type <class 'float'>.
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
            _check_docs(decorated_func=decorated_func)

        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            if decorated_func.is_instance_method and hasattr(args[0], TYPE_VAR_METHOD_NAME):
                type_vars = getattr(args[0], TYPE_VAR_METHOD_NAME)()
            else:
                type_vars = dict()

            _assert_uses_kwargs(func=decorated_func, args=args, is_class_decorator=is_class_decorator)
            return _check_types(decorated_func=decorated_func, args=args, kwargs=kwargs, type_vars=type_vars)
        return wrapper
    return decorator if func is None else decorator(f=func)


def pedantic_require_docstring(func: Optional[F] = None, **kwargs: Any) -> F:
    """Shortcut for @pedantic(require_docstring=True) """
    return pedantic(func=func, require_docstring=True, **kwargs)


def _check_types(decorated_func: DecoratedFunction,
                 args: Tuple[Any, ...],
                 kwargs: Dict[str, Any],
                 type_vars: Dict[TypeVar, Any]) -> Any:
    func = decorated_func.func
    params = decorated_func.signature.parameters
    err = decorated_func.err
    already_checked_kwargs = []
    arg_index = 1 if decorated_func.is_instance_method else 0
    params_without_self = {k: v for k, v in params.items() if v.name != 'self'}
    params_without_args_kwargs = {k: v for k, v in params_without_self.items() if not str(v).startswith('*')}

    for key in params_without_args_kwargs:
        param = params[key]
        expected_type = param.annotation

        if expected_type is inspect.Signature.empty:
            raise PedanticTypeCheckException(f'{err} Parameter "{param.name}" should have a type hint.')

        if param.default is inspect.Signature.empty:
            if decorated_func.should_have_kwargs:
                if key not in kwargs:
                    raise PedanticException(f'{err} Parameter "{key}" is unfilled.')
                actual_value = kwargs[key]
            else:
                actual_value = args[arg_index]
                arg_index += 1
        else:
            actual_value = kwargs[key] if key in kwargs else param.default

        if not _is_value_matching_type_hint(value=actual_value, type_hint=expected_type,
                                            err_prefix=err, type_vars=type_vars):
            raise PedanticTypeCheckException(f'{err} Type hint is incorrect: Passed Argument {key}={actual_value} does not have type {expected_type}.')

        already_checked_kwargs.append(key)

    _check_types_args(params=params_without_self, args=args, func=decorated_func, tv=type_vars)
    _check_types_kwargs(params=params_without_self, kwargs=kwargs, func=decorated_func, tv=type_vars,
                        ar=already_checked_kwargs)

    # _assert_has_return_annotation()
    if decorated_func.signature.return_annotation is inspect.Signature.empty:
        raise PedanticTypeCheckException(
            f'{err} There should be a type hint for the return type (e.g. None if nothing is returned).')

    result = func(*args, **kwargs) if not decorated_func.is_static_method else func(**kwargs)
    expected_result_type = decorated_func.annotations['return']

    if not _is_value_matching_type_hint(value=result, type_hint=expected_result_type,
                                        err_prefix=err, type_vars=type_vars):
        raise PedanticTypeCheckException(
            f'{err} Return type is incorrect: Expected {expected_result_type} '
            f'but {result} was the return value which does not match.')
    return result


def _check_types_args(params: Mapping[str, inspect.Parameter], args, func: DecoratedFunction, tv: Dict) -> None:
    """
    TODO doctests
    """

    params_args_only = {k: v for k, v in params.items() if str(v).startswith('*') and not str(v).startswith('**')}

    for param in params_args_only:
        expected_type = params_args_only[param].annotation
        for arg in args:
            if not _is_value_matching_type_hint(value=arg, type_hint=expected_type,
                                                err_prefix=func.err, type_vars=tv):
                raise PedanticTypeCheckException(
                    f'{func.err} Type hint is incorrect: Passed argument {arg} does not have type {expected_type}.')


def _check_types_kwargs(params: Mapping[str, inspect.Parameter], kwargs, func: DecoratedFunction, tv: Dict, ar) -> None:
    """
    TODO doctests
    """

    params_kwargs_only = {k: v for k, v in params.items() if str(v).startswith('**')}
    for param in params_kwargs_only:
        expected_type = params_kwargs_only[param].annotation

        if expected_type == inspect.Parameter.empty:
            raise PedanticTypeCheckException('TODO')

        for kwarg in kwargs:
            if kwarg in ar:
                continue

            actual_value = kwargs[kwarg]
            if not _is_value_matching_type_hint(value=actual_value, type_hint=expected_type,
                                                err_prefix=func.err, type_vars=tv):
                raise PedanticTypeCheckException(
                    f'{func.err} Type hint is incorrect: Passed Argument {kwarg}={actual_value} does not have type {expected_type}.')


def _check_docs(decorated_func: DecoratedFunction) -> None:
    doc = decorated_func.docstring
    err = decorated_func.err
    context = {}

    _assert_docstring_is_complete(func=decorated_func)

    for annotation in decorated_func.annotations:
        expected_type = decorated_func.annotations[annotation]
        _update_context(context=context, type_=expected_type)

        if annotation == 'return' and decorated_func.annotations[annotation] is not None:
            if len(doc.returns.args) != 2:
                raise PedanticDocstringException(f'{err} Parsing Error. Only Google style docstrings are supported.')

            actual_return_type = _parse_documented_type(type_=doc.returns.args[1], context=context, err=err)

            if actual_return_type != expected_type:
                raise PedanticDocstringException(
                    f'{err} Documented type is incorrect: Annotation: {expected_type} Documented: {actual_return_type}')
        elif annotation != 'return':
            docstring_param = list(filter(lambda p, a=annotation: p.arg_name == a, doc.params))[0]
            actual_param_type = _parse_documented_type(type_=docstring_param.type_name, context=context, err=err)

            if expected_type != actual_param_type:
                raise PedanticDocstringException(
                    f'{err} Documented type of parameter {annotation} is incorrect. Expected {expected_type} '
                    f'but documented is {actual_param_type}.')


def _assert_docstring_is_complete(func: DecoratedFunction) -> None:
    """
    TODO doctests
    """
    if func.raw_doc is None or func.raw_doc == '':
        raise PedanticDocstringException(f'{func.err} The function should have a docstring!')

    num_documented_args = len(func.docstring.params)
    num_taken_args = len([a for a in func.annotations if a != 'return'])

    if num_documented_args != num_taken_args:
        raise PedanticDocstringException(
            f'{func.err} There are {num_documented_args} argument(s) documented, '
            f'but {num_taken_args} are actually taken.')

    if func.docstring.returns is None and ('return' in func.annotations and func.annotations['return'] is not None):
        raise PedanticDocstringException(f'{func.err} The return type {func.annotations["return"]} is not documented.')

    if func.docstring.returns is not None and ('return' not in func.annotations or func.annotations['return'] is None):
        raise PedanticDocstringException(
            f'{func.err} The return type {func.docstring.returns.type_name} '
            f'is documented but the function does not return anything.')


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
    pedantic.exceptions.PedanticDocstringException:  Documented type "MyClass" was not found.
    >>> class MyClass: pass
    >>> _parse_documented_type(type_='MyClass', context={'MyClass': MyClass}, err='')
    <class 'pedantic.method_decorators.MyClass'>
    >>> _parse_documented_type(type_='MyClas', context={'MyClass': MyClass}, err='')
    Traceback (most recent call last):
    ...
    pedantic.exceptions.PedanticDocstringException:  Documented type "MyClas" was not found. Maybe you meant "MyClass"
    >>> class MyClub: pass
    >>> _parse_documented_type(type_='MyClas', context={'MyClass': MyClass, 'MyClub': MyClub}, err='')
    Traceback (most recent call last):
    ...
    pedantic.exceptions.PedanticDocstringException:  Documented type "MyClas" was not found. Maybe you meant one of the following: ['MyClass', 'MyClub']
    """

    if 'typing.' in type_:
        raise PedanticDocstringException(
            f'{err} Do not use "typing." in docstring. Please replace "{type_}" with '
            f'"{type_.replace("typing.", "")}" in  the docstring')

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
        raise PedanticDocstringException(f'{err} Documented type "{type_}" was not found.{msg}')


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
       pedantic.exceptions.PedanticCallWithArgsException: In function f2:
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
       pedantic.exceptions.PedanticCallWithArgsException: In function A.g:
        Use kwargs when you call function g. Args: (45,)
       >>> _assert_uses_kwargs(DecoratedFunction(A.__compare__), (a, 'hi',), False)
       >>> _assert_uses_kwargs(DecoratedFunction(A.__compare__), (a,), False)
    """
    if func.should_have_kwargs:
        args_without_self = _get_args_without_self(func=func, args=args, is_class_decorator=is_class_decorator)
        if args_without_self != ():
            raise PedanticCallWithArgsException(
                f'{func.err} Use kwargs when you call function {func.name}. Args: {args_without_self}')


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


def _is_value_matching_type_hint(value: Any, type_hint: Any, err_prefix: str, type_vars: Dict[TypeVar, Any]) -> bool:
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
        pedantic.exceptions.PedanticTypeCheckException:  Use "List[]" instead of "list" as type hint.
        >>> _is_value_matching_type_hint((1, 2, 3), tuple, '', {})
        Traceback (most recent call last):
        ...
        pedantic.exceptions.PedanticTypeCheckException:  Use "Tuple[]" instead of "tuple" as type hint.
        >>> _is_value_matching_type_hint({1: 1.0, 2: 2.0, 3: 3.0}, dict, '', {})
        Traceback (most recent call last):
        ...
        pedantic.exceptions.PedanticTypeCheckException:  Use "Dict[]" instead of "dict" as type hint.
    """

    if type_hint is None:
        return value == type_hint
    elif isinstance(type_hint, str):
        class_name = value.__class__.__name__
        return class_name == type_hint

    if type(type_hint) is tuple:
        raise PedanticTypeCheckException(f'{err_prefix} Use "Tuple[]" instead of "{type_hint}" as type hint.')
    if type_hint is tuple:
        raise PedanticTypeCheckException(f'{err_prefix} Use "Tuple[]" instead of "tuple" as type hint.')
    if type_hint is list:
        raise PedanticTypeCheckException(f'{err_prefix} Use "List[]" instead of "list" as type hint.')
    if type_hint is dict:
        raise PedanticTypeCheckException(f'{err_prefix} Use "Dict[]" instead of "dict" as type hint.')
    if type_hint is set:
        raise PedanticTypeCheckException(f'{err_prefix} Use "Set[]" instead of "set" as type hint.')
    if type_hint is frozenset:
        raise PedanticTypeCheckException(f'{err_prefix} Use "FrozenSet[]" instead of "frozenset" as type hint.')

    try:
        return _is_instance(obj=value, type_=type_hint, type_vars=type_vars)
    except PedanticTypeCheckException as ex:
        raise PedanticTypeCheckException(f'{err_prefix} {ex}')
    except PedanticTypeVarMismatchException as ex:
        raise PedanticTypeVarMismatchException(f'{err_prefix} {ex}')
    except (AttributeError, Exception) as ex:
        raise PedanticTypeCheckException(
            f'{err_prefix} An error occurred during type hint checking. Value: {value} Annotation: '
            f'{type_hint} Mostly this is caused by an incorrect type annotation. Details: {ex} ')


def _raise_warning(msg: str, category: Type[Warning]) -> None:
    warnings.simplefilter(action='always', category=category)
    warnings.warn(message=msg, category=category, stacklevel=2)
    warnings.simplefilter(action='default', category=category)


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
