"""Idea is taken from: https://stackoverflow.com/a/55504010/10975692"""
import inspect
import typing
from typing import Any, Dict, Iterable, ItemsView, Callable, Union, Optional, Tuple, Mapping, TypeVar, NewType
import collections
import sys

from pedantic.constants import TypeVar as TypeVar_
from pedantic.exceptions import PedanticTypeCheckException, PedanticTypeVarMismatchException, PedanticException


def _assert_value_matches_type(value: Any,
                               type_: Any,
                               err: str,
                               type_vars: Dict[TypeVar_, Any],
                               key: Optional[str] = None,
                               msg: Optional[str] = None
                               ) -> None:
    if not _check_type(value=value, type_=type_, err=err, type_vars=type_vars):
        t = type(value)
        value = f'{key}={value}'
        if not msg:
            msg = f'{err}Type hint is incorrect: Argument {value} of type {t} does not match expected type {type_}.'
        raise PedanticTypeCheckException(msg)


def _check_type(value: Any, type_: Any, err: str, type_vars: Dict[TypeVar_, Any]) -> bool:
    """
        >>> from typing import List, Union, Optional, Callable, Any
        >>> _check_type(5, int, '', {})
        True
        >>> _check_type(5, float, '', {})
        False
        >>> _check_type('hi', str, '', {})
        True
        >>> _check_type(None, str, '', {})
        False
        >>> _check_type(None, Any, '', {})
        True
        >>> _check_type(None, None, '', {})
        True
        >>> _check_type(5, Any, '', {})
        True
        >>> _check_type(3.1415, float, '', {})
        True
        >>> _check_type([1, 2, 3, 4], List[int], '', {})
        True
        >>> _check_type([1, 2, 3.0, 4], List[int], '', {})
        False
        >>> _check_type([1, 2, 3.0, 4], List[float], '', {})
        False
        >>> _check_type([1, 2, 3.0, 4], List[Union[float, int]], '', {})
        True
        >>> _check_type([[True, False], [False], [True], []], List[List[bool]], '', {})
        True
        >>> _check_type([[True, False, 1], [False], [True], []], List[List[bool]], '', {})
        False
        >>> _check_type(5, Union[int, float, bool], '', {})
        True
        >>> _check_type(5.0, Union[int, float, bool], '', {})
        True
        >>> _check_type(False, Union[int, float, bool], '', {})
        True
        >>> _check_type('5', Union[int, float, bool], '', {})
        False
        >>> def f(a: int, b: bool, c: str) -> float: pass
        >>> _check_type(f, Callable[[int, bool, str], float], '', {})
        True
        >>> _check_type(None, Optional[List[Dict[str, float]]], '', {})
        True
        >>> _check_type([{'a': 1.2, 'b': 3.4}], Optional[List[Dict[str, float]]], '', {})
        True
        >>> _check_type([{'a': 1.2, 'b': 3}], Optional[List[Dict[str, float]]], '', {})
        False
        >>> _check_type({'a': 1.2, 'b': 3.4}, Optional[List[Dict[str, float]]], '', {})
        False
        >>> _check_type([{'a': 1.2, 7: 3.4}], Optional[List[Dict[str, float]]], '', {})
        False
        >>> class MyClass: pass
        >>> _check_type(MyClass(), 'MyClass', '', {})
        True
        >>> _check_type(MyClass(), 'MyClas', '', {})
        False
        >>> _check_type([1, 2, 3], list, '', {})
        Traceback (most recent call last):
        ...
        pedantic.exceptions.PedanticTypeCheckException: Use "List[]" instead of "list" as type hint.
        >>> _check_type((1, 2, 3), tuple, '', {})
        Traceback (most recent call last):
        ...
        pedantic.exceptions.PedanticTypeCheckException: Use "Tuple[]" instead of "tuple" as type hint.
        >>> _check_type({1: 1.0, 2: 2.0, 3: 3.0}, dict, '', {})
        Traceback (most recent call last):
        ...
        pedantic.exceptions.PedanticTypeCheckException: Use "Dict[]" instead of "dict" as type hint.
    """

    if type_ is None:
        return value == type_
    elif isinstance(type_, str):
        class_name = value.__class__.__name__
        return class_name == type_

    if type(type_) is tuple:
        raise PedanticTypeCheckException(f'{err}Use "Tuple[]" instead of "{type_}" as type hint.')
    if type_ is tuple:
        raise PedanticTypeCheckException(f'{err}Use "Tuple[]" instead of "tuple" as type hint.')
    if type_ is list:
        raise PedanticTypeCheckException(f'{err}Use "List[]" instead of "list" as type hint.')
    if type_ is dict:
        raise PedanticTypeCheckException(f'{err}Use "Dict[]" instead of "dict" as type hint.')
    if type_ is set:
        raise PedanticTypeCheckException(f'{err}Use "Set[]" instead of "set" as type hint.')
    if type_ is frozenset:
        raise PedanticTypeCheckException(f'{err}Use "FrozenSet[]" instead of "frozenset" as type hint.')

    try:
        return _is_instance(obj=value, type_=type_, type_vars=type_vars)
    except PedanticTypeCheckException as ex:
        raise PedanticTypeCheckException(f'{err} {ex}')
    except PedanticTypeVarMismatchException as ex:
        raise PedanticTypeVarMismatchException(f'{err} {ex}')
    except (AttributeError, Exception) as ex:
        raise PedanticTypeCheckException(
            f'{err}An error occurred during type hint checking. Value: {value} Annotation: '
            f'{type_} Mostly this is caused by an incorrect type annotation. Details: {ex} ')


def _is_instance(obj: Any, type_: Any, type_vars: Dict[TypeVar_, Any]) -> bool:
    if not _has_required_type_arguments(type_):
        raise PedanticTypeCheckException(
            f'The type annotation "{type_}" misses some type arguments e.g. '
            f'"typing.Tuple[Any, ...]" or "typing.Callable[..., str]".')

    if type_.__module__ == 'typing':
        if _is_generic(type_):
            origin = _get_base_generic(type_)
        else:
            origin = type_
        name = _get_name(origin)

        if name in _SPECIAL_INSTANCE_CHECKERS:
            validator = _SPECIAL_INSTANCE_CHECKERS[name]
            return validator(obj, type_, type_vars)

    if _is_generic(type_):
        python_type = type_.__origin__
        if not isinstance(obj, python_type):
            return False

        base = _get_base_generic(type_)
        validator = _ORIGIN_TYPE_CHECKERS[base]

        type_args = _get_type_arguments(cls=type_)
        return validator(obj, type_args, type_vars)

    if isinstance(type_, TypeVar):
        if type_ in type_vars:
            other = type_vars[type_]
            if not _is_instance(obj=obj, type_=other, type_vars=type_vars):
                raise PedanticTypeVarMismatchException(
                    f'For TypeVar {type_} exists a type conflict: value {obj} has type {type(obj)} but TypeVar {type_} '
                    f'was previously matched to type {other}')
        type_vars[type_] = type(obj)
        return True

    if _is_type_new_type(type_):
        return isinstance(obj, type_.__supertype__)
    return isinstance(obj, type_)


def _is_type_new_type(type_: Any) -> bool:
    """
        >>> from typing import Tuple, Callable, Any, List, NewType
        >>> _is_type_new_type(int)
        False
        >>> UserId = NewType('UserId', int)
        >>> _is_type_new_type(UserId)
        True
    """
    return type_.__qualname__ == NewType('name', int).__qualname__  # arguments of NewType() are arbitrary here


def _get_name(cls: Any) -> str:
    """
        >>> from typing import Tuple, Callable, Any, List
        >>> _get_name(int)
        'int'
        >>> _get_name(Any)
        'Any'
        >>> _get_name(List)
        'List'
        >>> _get_name(List[int])
        'List'
        >>> _get_name(List[Any])
        'List'
        >>> _get_name(Tuple)
        'Tuple'
        >>> _get_name(Tuple[int, float])
        'Tuple'
        >>> _get_name(Tuple[Any, ...])
        'Tuple'
        >>> _get_name(Callable)
        'Callable'
    """
    if hasattr(cls, '_name'):
        return cls._name
    elif hasattr(cls, '__name__'):
        return cls.__name__
    else:
        return type(cls).__name__[1:]


def _is_generic(cls: Any) -> bool:
    """
        >>> from typing import  List, Callable, Any, Union
        >>> _is_generic(int)
        False
        >>> _is_generic(List)
        True
        >>> _is_generic(List[int])
        True
        >>> _is_generic(List[Any])
        True
        >>> _is_generic(List[List[int]])
        True
        >>> _is_generic(Any)
        False
        >>> _is_generic(Tuple)
        True
        >>> _is_generic(Tuple[Any, ...])
        True
        >>> _is_generic(Tuple[str, float, int])
        True
        >>> _is_generic(Callable)
        True
        >>> _is_generic(Callable[[int], int])
        True
        >>> _is_generic(Union)
        True
        >>> _is_generic(Union[int, float, str])
        True
        >>> _is_generic(Dict)
        True
        >>> _is_generic(Dict[str, str])
        True
    """
    if hasattr(typing, '_SpecialGenericAlias') and isinstance(cls, typing._SpecialGenericAlias):
        return True
    elif hasattr(typing, '_GenericAlias'):
        if isinstance(cls, typing._GenericAlias):
            return True

        if isinstance(cls, typing._SpecialForm):
            return cls not in {Any}
    elif isinstance(cls, (typing.GenericMeta, typing._Union, typing._Optional, typing._ClassVar)):
        return True
    return False


def _has_required_type_arguments(cls: Any) -> bool:
    """
        >>> from typing import List, Callable, Tuple, Any
        >>> _has_required_type_arguments(int)
        True
        >>> _has_required_type_arguments(List)
        False
        >>> _has_required_type_arguments(List[int])
        True
        >>> _has_required_type_arguments(List[List[int]])
        True
        >>> _has_required_type_arguments(Tuple)
        False
        >>> _has_required_type_arguments(Tuple[int])
        True
        >>> _has_required_type_arguments(Tuple[int, float, str])
        True
        >>> _has_required_type_arguments(Callable)
        False
        >>> _has_required_type_arguments(Callable[[int, float], Tuple[float, str]])
        True
        >>> _has_required_type_arguments(Callable[..., Any])
        True
        >>> _has_required_type_arguments(Callable[[typing.Any], Tuple[typing.Any, ...]],)
        True
    """

    base: str = _get_name(cls=cls)
    num_type_args = len(_get_type_arguments(cls=cls))

    if base in NUM_OF_REQUIRED_TYPE_ARGS_EXACT:
        return NUM_OF_REQUIRED_TYPE_ARGS_EXACT[base] == num_type_args
    elif base in NUM_OF_REQUIRED_TYPE_ARGS_MIN:
        return NUM_OF_REQUIRED_TYPE_ARGS_MIN[base] <= num_type_args
    return True


def _get_type_arguments(cls: Any) -> Tuple[Any, ...]:
    """ Works similar to typing.args()
        >>> from typing import Tuple, List, Union, Callable, Any, NewType, TypeVar, Optional
        >>> _get_type_arguments(int)
        ()
        >>> _get_type_arguments(List[float])
        (<class 'float'>,)
        >>> _get_type_arguments(List[int])
        (<class 'int'>,)
        >>> UserId = NewType('UserId', int)
        >>> _get_type_arguments(List[UserId])
        (<function NewType.<locals>.new_type at ...,)
        >>> _get_type_arguments(List)
        ()
        >>> T = TypeVar('T')
        >>> _get_type_arguments(List[T])
        (~T,)
        >>> _get_type_arguments(List[List[int]])
        (typing.List[int],)
        >>> _get_type_arguments(List[List[List[int]]])
        (typing.List[typing.List[int]],)
        >>> _get_type_arguments(List[Tuple[float, str]])
        (typing.Tuple[float, str],)
        >>> _get_type_arguments(List[Tuple[Any, ...]])
        (typing.Tuple[typing.Any, ...],)
        >>> Union[bool, int, float] if sys.version_info >= (3, 7) else \
            print("typing.Union[bool, int, float]") # in Python 3.6 is bool an subtype of int, WTF!?
        typing.Union[bool, int, float]
        >>> _get_type_arguments(Union[str, float, int])
        (<class 'str'>, <class 'float'>, <class 'int'>)
        >>> _get_type_arguments(Union[str, float, List[int], int])
        (<class 'str'>, <class 'float'>, typing.List[int], <class 'int'>)
        >>> _get_type_arguments(Callable)
        ()
        >>> _get_type_arguments(Callable[[int, float], Tuple[float, str]])
        ([<class 'int'>, <class 'float'>], typing.Tuple[float, str])
        >>> _get_type_arguments(Callable[..., str])
        (Ellipsis, <class 'str'>)
        >>> _get_type_arguments(Optional[int])
        (<class 'int'>, <class 'NoneType'>)
    """

    result = ()

    if hasattr(cls, '__args__'):
        result = cls.__args__
        origin = _get_base_generic(cls=cls)
        if origin != cls and \
                ((origin is Callable) or (origin is collections.abc.Callable)) and \
                result[0] is not Ellipsis:
            result = (list(result[:-1]), result[-1])
    result = result or ()
    return result if '[' in str(cls) else ()


def _get_base_generic(cls: Any) -> Any:
    """
        >>> from typing import List, Union, Tuple, Callable, Dict, Set
        >>> _get_base_generic(List)
        typing.List
        >>> _get_base_generic(List[float])
        typing.List
        >>> _get_base_generic(List[List[float]])
        typing.List
        >>> _get_base_generic(List[Union[int, float]])
        typing.List
        >>> _get_base_generic(Tuple)
        typing.Tuple
        >>> _get_base_generic(Tuple[float, int])
        typing.Tuple
        >>> _get_base_generic(Tuple[Union[int, float], str])
        typing.Tuple
        >>> _get_base_generic(Callable[..., int])
        typing.Callable
        >>> _get_base_generic(Callable[[Union[int, str], float], int])
        typing.Callable
        >>> _get_base_generic(Dict)
        typing.Dict
        >>> _get_base_generic(Dict[str, str])
        typing.Dict
        >>> _get_base_generic(Union)
        typing.Union
        >>> _get_base_generic(Union[float, int, str])
        typing.Union
        >>> _get_base_generic(Set)
        typing.Set
        >>> _get_base_generic(Set[int])
        typing.Set
    """

    origin = cls.__origin__ if hasattr(cls, '__origin__') else None
    name = cls._name if hasattr(cls, '_name') else None

    if name is not None:
        return getattr(typing, name)
    elif origin is not None:
        return origin
    return cls


def _is_subtype(sub_type: Any, super_type: Any) -> bool:
    """
        >>> from typing import Any, List, Callable, Tuple, Union, Optional, Iterable
        >>> _is_subtype(float, float)
        True
        >>> _is_subtype(int, float)
        False
        >>> _is_subtype(float, int)
        False
        >>> _is_subtype(int, Any)
        True
        >>> _is_subtype(Any, int)
        False
        >>> _is_subtype(Any, Any)
        True
        >>> _is_subtype(Ellipsis, Ellipsis)
        True
        >>> _is_subtype(Tuple[float, str], Tuple[float, str])
        True
        >>> _is_subtype(Tuple[float], Tuple[float, str])
        False
        >>> _is_subtype(Tuple[float, str], Tuple[str])
        False
        >>> _is_subtype(Tuple[float, str], Tuple[Any, ...])
        True
        >>> _is_subtype(Tuple[Any, ...], Tuple[float, str])
        False
        >>> _is_subtype(Tuple[float, str], Tuple[int, ...])
        False
        >>> _is_subtype(Tuple[int, str], Tuple[int, ...])
        True
        >>> _is_subtype(Tuple[int, ...], Tuple[int, str])
        False
        >>> _is_subtype(Tuple[float, str, bool, int], Tuple[Any, ...])
        True
        >>> _is_subtype(int, Union[int, float])
        Traceback (most recent call last):
        ...
        TypeError: ...
        >>> _is_subtype(int, Union[str, float])
        Traceback (most recent call last):
        ...
        TypeError: ...
        >>> _is_subtype(List[int], List[Union[int, float]])
        Traceback (most recent call last):
        ...
        TypeError: ...
        >>> _is_subtype(List[Union[int, float]], List[int])
        Traceback (most recent call last):
        ...
        TypeError: issubclass() arg 1 must be a class
        >>> class Parent: pass
        >>> class Child(Parent): pass
        >>> _is_subtype(List[Child], List[Parent])
        True
        >>> _is_subtype(List[Parent], List[Child])
        False
        >>> _is_subtype(List[int], Iterable[int])
        True
        >>> _is_subtype(Iterable[int], List[int])
        False
    """

    python_sub = _get_class_of_type_annotation(sub_type)
    python_super = _get_class_of_type_annotation(super_type)

    if not _is_generic(sub_type):
        return issubclass(python_sub, python_super)

    if not issubclass(python_sub, python_super):
        return False

    if not _is_generic(super_type):
        return True

    sub_args = _get_type_arguments(cls=sub_type)
    super_args = _get_type_arguments(cls=super_type)

    if len(sub_args) != len(super_args) and Ellipsis not in sub_args + super_args:
        return False
    return all(_is_subtype(sub_type=sub_arg, super_type=super_arg) for sub_arg, super_arg in zip(sub_args, super_args))


def _get_class_of_type_annotation(annotation: Any) -> Any:
    """
        >>> from typing import Dict, List, Any, Tuple, Callable, Union
        >>> _get_class_of_type_annotation(int)
        <class 'int'>
        >>> _get_class_of_type_annotation(Any)
        <class 'object'>
        >>> _get_class_of_type_annotation(Ellipsis)
        <class 'object'>
        >>> _get_class_of_type_annotation(Dict)
        <class 'dict'>
        >>> _get_class_of_type_annotation(Dict[str, int])
        <class 'dict'>
        >>> _get_class_of_type_annotation(List)
        <class 'list'>
        >>> _get_class_of_type_annotation(List[int])
        <class 'list'>
        >>> _get_class_of_type_annotation(Tuple)
        <class 'tuple'>
        >>> _get_class_of_type_annotation(Tuple[int, int])
        <class 'tuple'>
        >>> _get_class_of_type_annotation(Callable[[int], int])
        <class 'collections.abc.Callable'>
        >>> _get_class_of_type_annotation(Callable)
        <class 'collections.abc.Callable'>
    """
    if annotation in [Any, Ellipsis]:
        return object
    elif hasattr(annotation, '__extra__'):
        return annotation.__extra__
    elif annotation.__module__ == 'typing' and annotation.__origin__ is not None:
        return annotation.__origin__
    else:
        return annotation


def _instancecheck_iterable(iterable: Iterable, type_args: Tuple, type_vars: Dict[TypeVar_, Any]) -> bool:
    """
        >>> from typing import List, Any, Union
        >>> _instancecheck_iterable([1.0, -4.2, 5.4], (float,), {})
        True
        >>> _instancecheck_iterable([1.0, -4.2, 5], (float,), {})
        False
        >>> _instancecheck_iterable(['1.0', -4.2, 5], (Any,), {})
        True
        >>> _instancecheck_iterable(['1.0', -4.2, 5], (Union[int, float],), {})
        False
        >>> _instancecheck_iterable(['1.0', -4.2, 5], (Union[int, float, str],), {})
        True
        >>> _instancecheck_iterable([[], [], [[42]], [[]]], (List[int],), {})
        False
        >>> _instancecheck_iterable([[], [], [[42]], [[]]], (List[List[int]],), {})
        True
        >>> _instancecheck_iterable([[], [], [[42]], [[]]], (List[List[float]],), {})
        False
    """
    type_ = type_args[0]
    return all(_is_instance(val, type_, type_vars=type_vars) for val in iterable)


def _instancecheck_mapping(mapping: Mapping, type_args: Tuple, type_vars: Dict[TypeVar_, Any]) -> bool:
    """
        >>> from typing import Any, Optional
        >>> _instancecheck_mapping({0: 1, 1: 2, 2: 3}, (int, Any), {})
        True
        >>> _instancecheck_mapping({0: 1, 1: 2, 2: 3}, (int, int), {})
        True
        >>> _instancecheck_mapping({0: 1, 1: 2, 2: 3.0}, (int, int), {})
        False
        >>> _instancecheck_mapping({0: 1, 1.0: 2, 2: 3}, (int, int), {})
        False
        >>> _instancecheck_mapping({0: '1', 1: 2, 2: 3}, (int, int), {})
        False
        >>> _instancecheck_mapping({0: 1, 1: 2, None: 3.0}, (int, int), {})
        False
        >>> _instancecheck_mapping({0: 1, 1: 2, None: 3.0}, (int, Optional[int]), {})
        False
    """
    return _instancecheck_items_view(mapping.items(), type_args, type_vars=type_vars)


def _instancecheck_items_view(items_view: ItemsView, type_args: Tuple, type_vars: Dict[TypeVar_, Any]) -> bool:
    """
        >>> from typing import Any, Optional
        >>> _instancecheck_items_view({0: 1, 1: 2, 2: 3}.items(), (int, Any), {})
        True
        >>> _instancecheck_items_view({0: 1, 1: 2, 2: 3}.items(), (int, int), {})
        True
        >>> _instancecheck_items_view({0: 1, 1: 2, 2: 3.0}.items(), (int, int), {})
        False
        >>> _instancecheck_items_view({0: 1, 1.0: 2, 2: 3}.items(), (int, int), {})
        False
        >>> _instancecheck_items_view({0: '1', 1: 2, 2: 3}.items(), (int, int), {})
        False
        >>> _instancecheck_items_view({0: 1, 1: 2, None: 3.0}.items(), (int, int), {})
        False
        >>> _instancecheck_items_view({0: 1, 1: 2, None: 3.0}.items(), (int, Optional[int]), {})
        False
    """
    key_type, value_type = type_args
    return all(_is_instance(obj=key, type_=key_type, type_vars=type_vars) and
               _is_instance(obj=val, type_=value_type, type_vars=type_vars)
               for key, val in items_view)


def _instancecheck_tuple(tup: Tuple, type_args: Any, type_vars: Dict[TypeVar_, Any]) -> bool:
    """
        >>> from typing import Any
        >>> _instancecheck_tuple(tup=(42.0, 43, 'hi', 'you'), type_args=(Any, Ellipsis), type_vars={})
        True
        >>> _instancecheck_tuple(tup=(42.0, 43, 'hi', 'you'), type_args=(Any,), type_vars={})
        False
        >>> _instancecheck_tuple(tup=(42.0, 43, 'hi', 'you'), type_args=(float, int, str, str), type_vars={})
        True
        >>> _instancecheck_tuple(tup=(42.0, 43, 'hi', 'you'), type_args=(float, float, str, str), type_vars={})
        False
        >>> _instancecheck_tuple(tup=(42.0, 43, 'hi', 'you'), type_args=(float, int, str, int), type_vars={})
        False
    """
    if Ellipsis in type_args:
        return all(_is_instance(obj=val, type_=type_args[0], type_vars=type_vars) for val in tup)

    if len(tup) != len(type_args):
        return False

    return all(_is_instance(obj=val, type_=type_, type_vars=type_vars) for val, type_ in zip(tup, type_args))


def _instancecheck_union(value: Any, type_: Any, type_vars: Dict[TypeVar_, Any]) -> bool:
    """
        >>> from typing import Union, TypeVar, Any
        >>> NoneType = type(None)
        >>> _instancecheck_union(3.0, Union[int, float], {})
        True
        >>> _instancecheck_union(3, Union[int, float], {})
        True
        >>> _instancecheck_union('3', Union[int, float], {})
        False
        >>> _instancecheck_union(None, Union[int, NoneType], {})
        True
        >>> _instancecheck_union(None, Union[float, NoneType], {})
        True
        >>> S = TypeVar('S')
        >>> T = TypeVar('T')
        >>> U = TypeVar('U')
        >>> _instancecheck_union(42, Union[T, NoneType], {})
        True
        >>> _instancecheck_union(None, Union[T, NoneType], {})
        True
        >>> _instancecheck_union(None, Union[T, NoneType], {T: int})
        True
        >>> _instancecheck_union('None', Union[T, NoneType], {T: int})
        False
        >>> _instancecheck_union(42, Union[T, S], {})
        True
        >>> _instancecheck_union(42, Union[T, S], {T: int})
        True
        >>> _instancecheck_union(42, Union[T, S], {T: str})
        True
        >>> _instancecheck_union(42, Union[T, S], {T: int, S: float})
        True
        >>> _instancecheck_union(42, Union[T, S], {T: str, S: float})
        False
        >>> _instancecheck_union(42.8, Union[T, S], {T: str, S: float})
        True
        >>> _instancecheck_union(None, Union[T, S], {T: str, S: float})
        False
        >>> _instancecheck_union(None, Union[T, S], {})
        True
        >>> _instancecheck_union(None, Union[T, NoneType], {T: int})
        True
        >>> _instancecheck_union('None', Union[T, NoneType, S], {T: int})
        True
        >>> _instancecheck_union(42, Union[T, Any], {})
        True
        >>> _instancecheck_union(42, Union[T, Any], {T: float})
        True
    """

    type_args = _get_type_arguments(cls=type_)
    args_non_type_vars = [type_arg for type_arg in type_args if not isinstance(type_arg, TypeVar)]
    args_type_vars = [type_arg for type_arg in type_args if isinstance(type_arg, TypeVar)]
    args_type_vars_bounded = [type_var for type_var in args_type_vars if type_var in type_vars]
    args_type_vars_unbounded = [type_var for type_var in args_type_vars if type_var not in args_type_vars_bounded]
    matches_non_type_var = any(_is_instance(obj=value, type_=typ, type_vars=type_vars) for typ in args_non_type_vars)
    if matches_non_type_var:
        return True

    for bounded_type_var in args_type_vars_bounded:
        try:
            _is_instance(obj=value, type_=bounded_type_var, type_vars=type_vars)
            return True
        except PedanticException:
            pass

    if not args_type_vars_unbounded:
        return False
    if len(args_type_vars_unbounded) == 1:
        return _is_instance(obj=value, type_=args_type_vars_unbounded[0], type_vars=type_vars)
    return True  # it is impossible to figure out, how to bound these type variables correctly


def _instancecheck_callable(value: Callable, type_: Any, _) -> bool:
    """
        >>> from typing import Tuple, Callable, Any
        >>> def f(x: int, y: float) -> Tuple[float, str]:
        ...       return float(x), str(y)
        >>> _instancecheck_callable(f, Callable[[int, float], Tuple[float, str]], {})
        True
        >>> _instancecheck_callable(f, Callable[[int, float], Tuple[int, str]], {})
        False
        >>> _instancecheck_callable(f, Callable[[int, int], Tuple[float, str]], {})
        False
        >>> _instancecheck_callable(f, Callable[..., Tuple[float, str]], {})
        True
        >>> _instancecheck_callable(f, Callable[..., Tuple[int, str]], {})
        False
        >>> _instancecheck_callable(f, Callable[..., Any], {})
        True
        >>> _instancecheck_callable(f, Callable[[int, int, int], Tuple[float, str]], {})
        False
    """
    param_types, ret_type = _get_type_arguments(cls=type_)
    sig = inspect.signature(obj=value)
    missing_annotations = []

    if param_types is not ...:
        if len(param_types) != len(sig.parameters):
            return False

        for param, expected_type in zip(sig.parameters.values(), param_types):
            param_type = param.annotation
            if param_type is inspect.Parameter.empty:
                missing_annotations.append(param)
                continue

            if not _is_subtype(sub_type=param_type, super_type=expected_type):
                return False

    if sig.return_annotation is inspect.Signature.empty:
        missing_annotations.append('return')
    else:
        if not _is_subtype(sub_type=sig.return_annotation, super_type=ret_type):
            return False

    if missing_annotations:
        raise PedanticTypeCheckException(
            f'Parsing of type annotations failed. Maybe you are about to return a lambda expression. '
            f'Try returning an inner function instead. {missing_annotations}')
    return True


_ORIGIN_TYPE_CHECKERS = {}
for class_path, _check_func in {
    'typing.Container': _instancecheck_iterable,
    'typing.Collection': _instancecheck_iterable,
    'typing.AbstractSet': _instancecheck_iterable,
    'typing.MutableSet': _instancecheck_iterable,
    'typing.Sequence': _instancecheck_iterable,
    'typing.MutableSequence': _instancecheck_iterable,
    'typing.ByteString': _instancecheck_iterable,
    'typing.Deque': _instancecheck_iterable,
    'typing.List': _instancecheck_iterable,
    'typing.Set': _instancecheck_iterable,
    'typing.FrozenSet': _instancecheck_iterable,
    'typing.KeysView': _instancecheck_iterable,
    'typing.ValuesView': _instancecheck_iterable,
    'typing.AsyncIterable': _instancecheck_iterable,

    'typing.Mapping': _instancecheck_mapping,
    'typing.MutableMapping': _instancecheck_mapping,
    'typing.MappingView': _instancecheck_mapping,
    'typing.ItemsView': _instancecheck_items_view,
    'typing.Dict': _instancecheck_mapping,
    'typing.DefaultDict': _instancecheck_mapping,
    'typing.Counter': _instancecheck_mapping,
    'typing.ChainMap': _instancecheck_mapping,

    'typing.Tuple': _instancecheck_tuple,
}.items():
    class_ = eval(class_path)
    _ORIGIN_TYPE_CHECKERS[class_] = _check_func

_SPECIAL_INSTANCE_CHECKERS = {
    'Union': _instancecheck_union,
    'Callable': _instancecheck_callable,
    'Any': lambda v, t, tv: True,
}

NUM_OF_REQUIRED_TYPE_ARGS_EXACT = {
    'Callable': 2,
    'List': 1,
    'Set': 1,
    'FrozenSet': 1,
    'Iterable': 1,
    'Sequence': 1,
    'Dict': 2,
    'Optional': 2,  # because _get_type_arguments(Optional[int]) returns (int, None)
}
NUM_OF_REQUIRED_TYPE_ARGS_MIN = {
    'Tuple': 1,
    'Union': 2,
}


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
