from typing import *  # necessary for eval()

from pedantic.type_checking_logic.check_types import _get_type_arguments
from pedantic.exceptions import PedanticDocstringException
from pedantic.models.decorated_function import DecoratedFunction


def _check_docstring(decorated_func: DecoratedFunction) -> None:
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
        >>> def f1(): pass
        >>> _assert_docstring_is_complete(DecoratedFunction(f1))
        Traceback (most recent call last):
        ...
        pedantic.exceptions.PedanticDocstringException: In function f1:
         The function should have a docstring!
        >>> def f2():
        ...     ''' This is a docstring. '''
        ...     pass
        >>> _assert_docstring_is_complete(DecoratedFunction(f2))
        >>> def f3() -> None:
        ...     ''' This is a docstring. '''
        ...     pass
        >>> _assert_docstring_is_complete(DecoratedFunction(f3))
        >>> def f4() -> int:
        ...     ''' This is a docstring. '''
        ...     return 42
        >>> _assert_docstring_is_complete(DecoratedFunction(f4))
        Traceback (most recent call last):
        ...
        pedantic.exceptions.PedanticDocstringException: In function f4:
         The return type <class 'int'> is not documented.
        >>> def f5() -> int:
        ...     ''' This is a docstring.
        ...     Returns:
        ...         int: a magic number
        ...     '''
        ...     return 42
        >>> _assert_docstring_is_complete(DecoratedFunction(f5))
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
    pedantic.exceptions.PedanticDocstringException: Documented type "MyClass" was not found.
    >>> class MyClass: pass
    >>> _parse_documented_type(type_='MyClass', context={'MyClass': MyClass}, err='')
    <class 'pedantic.type_checking_logic.check_docstring.MyClass'>
    >>> _parse_documented_type(type_='MyClas', context={'MyClass': MyClass}, err='')
    Traceback (most recent call last):
    ...
    pedantic.exceptions.PedanticDocstringException: Documented type "MyClas" was not found. Maybe you meant "MyClass"
    >>> class MyClub: pass
    >>> _parse_documented_type(type_='MyClas', context={'MyClass': MyClass, 'MyClub': MyClub}, err='')
    Traceback (most recent call last):
    ...
    pedantic.exceptions.PedanticDocstringException: Documented type "MyClas" was not found. Maybe you meant one of the following: ['MyClass', 'MyClub']
    """

    if 'typing.' in type_:
        raise PedanticDocstringException(
            f'{err}Do not use "typing." in docstring. Please replace "{type_}" with '
            f'"{type_.replace("typing.", "")}" in the docstring')

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
        raise PedanticDocstringException(f'{err}Documented type "{type_}" was not found.{msg}')


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
